#!/usr/bin/env python3
"""abtest.py - A/B test design and analysis calculator (stdlib only).

Provides sample-size planning and the common significance tests used in
online experiments. No third-party dependencies (no scipy/numpy required);
the normal and t distributions are approximated with high-accuracy stdlib math.

Usage:
  python abtest.py size  --baseline 0.10 --mde-rel 0.05 [--alpha 0.05] [--power 0.80] [--two-sided/--one-sided]
  python abtest.py size  --baseline 0.10 --mde-abs 0.005
  python abtest.py prop  --c-conv 5800 --c-n 58000 --t-conv 6150 --t-n 58000 [--alpha 0.05]
  python abtest.py ttest --c-mean 50.2 --c-sd 18.0 --c-n 4000 --t-mean 51.5 --t-sd 18.4 --t-n 4010
  python abtest.py chisq --counts 100,900 130,870 120,880   (each pair = conv,non-conv per variant)
  python abtest.py srm   --observed 50100,49900 --split 0.5,0.5

All commands print a human-readable summary. Exit code is 0 on success.
"""
import argparse
import math
import sys


# ---------------------------------------------------------------------------
# Distribution helpers (stdlib only)
# ---------------------------------------------------------------------------
def norm_cdf(x):
    """Standard normal CDF via the error function."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def norm_sf(x):
    """Survival function 1 - CDF."""
    return 1.0 - norm_cdf(x)


def norm_ppf(p):
    """Inverse standard normal CDF (quantile). Acklam's algorithm."""
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0,1)")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5]) * q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    """Regularized incomplete beta function I_x(a,b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_sf(t, df):
    """Survival function P(T > t) for Student's t with df degrees of freedom."""
    x = df / (df + t * t)
    half = 0.5 * _betai(df / 2.0, 0.5, x)
    return half if t > 0 else 1.0 - half


def chisq_sf(x, k):
    """Survival function of chi-square with k df via regularized upper gamma."""
    if x <= 0:
        return 1.0
    return _gammaincc(k / 2.0, x / 2.0)


def _gammaincc(a, x):
    """Regularized upper incomplete gamma Q(a,x)."""
    if x < a + 1.0:
        return 1.0 - _gammp_series(a, x)
    return _gammq_cf(a, x)


def _gammp_series(a, x, itmax=300, eps=3e-14):
    if x <= 0:
        return 0.0
    ap = a
    s = 1.0 / a
    delta = s
    for _ in range(itmax):
        ap += 1.0
        delta *= x / ap
        s += delta
        if abs(delta) < abs(s) * eps:
            break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gammq_cf(a, x, itmax=300, eps=3e-14):
    b = x + 1.0 - a
    c = 1e30
    d = 1.0 / b
    h = d
    for i in range(1, itmax + 1):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < 1e-30:
            d = 1e-30
        c = b + an / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < eps:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_size(args):
    p1 = args.baseline
    if not 0.0 < p1 < 1.0:
        sys.exit("--baseline must be a proportion in (0,1)")
    if args.mde_abs is not None:
        delta = args.mde_abs
    elif args.mde_rel is not None:
        delta = p1 * args.mde_rel
    else:
        sys.exit("provide --mde-rel or --mde-abs")
    p2 = p1 + delta
    if not 0.0 < p2 < 1.0:
        sys.exit("baseline + MDE is outside (0,1); reduce the MDE")
    alpha = args.alpha
    power = args.power
    z_alpha = norm_ppf(1 - alpha / (1 if args.one_sided else 2))
    z_beta = norm_ppf(power)
    pbar = (p1 + p2) / 2.0
    # Standard two-proportion sample-size formula (per arm, equal allocation).
    num = (z_alpha * math.sqrt(2 * pbar * (1 - pbar)) +
           z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = num / (delta ** 2)
    n_arm = math.ceil(n)
    print("Sample size planning (two-proportion)")
    print("-" * 42)
    print(f"  baseline rate        : {p1:.4%}")
    print(f"  target rate          : {p2:.4%}")
    print(f"  MDE (absolute)       : {delta:+.4%}")
    print(f"  MDE (relative)       : {delta / p1:+.2%}")
    print(f"  alpha / power        : {alpha} / {power}")
    print(f"  sided                : {'one' if args.one_sided else 'two'}-sided")
    print(f"  REQUIRED N per arm   : {n_arm:,}")
    print(f"  REQUIRED N total     : {n_arm * 2:,}")
    if args.daily_per_arm:
        days = math.ceil(n_arm / args.daily_per_arm)
        weeks = math.ceil(days / 7)
        print(f"  est. duration        : {days} days (round to {weeks} full week(s))")


def _wilson_or_wald_ci(diff, se, alpha):
    z = norm_ppf(1 - alpha / 2)
    return diff - z * se, diff + z * se


def cmd_prop(args):
    x1, n1 = args.c_conv, args.c_n
    x2, n2 = args.t_conv, args.t_n
    if x1 > n1 or x2 > n2:
        sys.exit("conversions cannot exceed n")
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1
    pooled = (x1 + x2) / (n1 + n2)
    se_pooled = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = diff / se_pooled if se_pooled > 0 else 0.0
    pval = 2 * norm_sf(abs(z))
    se_unpooled = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    lo, hi = _wilson_or_wald_ci(diff, se_unpooled, args.alpha)
    rel = diff / p1 if p1 > 0 else float('nan')
    print("Two-proportion z-test")
    print("-" * 42)
    print(f"  control            : {x1:,}/{n1:,} = {p1:.4%}")
    print(f"  treatment          : {x2:,}/{n2:,} = {p2:.4%}")
    print(f"  absolute lift      : {diff:+.4%}")
    print(f"  relative lift      : {rel:+.2%}")
    print(f"  {int((1-args.alpha)*100)}% CI (absolute) : [{lo:+.4%}, {hi:+.4%}]")
    print(f"  z statistic        : {z:.4f}")
    print(f"  p-value (2-sided)  : {pval:.6f}")
    sig = pval < args.alpha
    print(f"  result             : {'SIGNIFICANT' if sig else 'not significant'} at alpha={args.alpha}")
    if sig and lo <= 0 <= hi:
        print("  note               : CI straddles 0 numerically; double-check inputs")
    print("  reminder           : decide using the CI + business value, not the p-value alone")


def cmd_ttest(args):
    m1, s1, n1 = args.c_mean, args.c_sd, args.c_n
    m2, s2, n2 = args.t_mean, args.t_sd, args.t_n
    v1, v2 = s1 ** 2 / n1, s2 ** 2 / n2
    se = math.sqrt(v1 + v2)
    diff = m2 - m1
    t = diff / se if se > 0 else 0.0
    # Welch-Satterthwaite degrees of freedom
    df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1))
    pval = 2 * t_sf(abs(t), df)
    z = norm_ppf(1 - args.alpha / 2)
    lo, hi = diff - z * se, diff + z * se
    rel = diff / m1 if m1 != 0 else float('nan')
    print("Welch's t-test (difference of means)")
    print("-" * 42)
    print(f"  control mean       : {m1:.4f} (sd {s1:.4f}, n {n1:,})")
    print(f"  treatment mean     : {m2:.4f} (sd {s2:.4f}, n {n2:,})")
    print(f"  absolute diff      : {diff:+.4f}")
    print(f"  relative diff      : {rel:+.2%}")
    print(f"  {int((1-args.alpha)*100)}% CI (approx)   : [{lo:+.4f}, {hi:+.4f}]")
    print(f"  t statistic        : {t:.4f}  (df {df:.1f})")
    print(f"  p-value (2-sided)  : {pval:.6f}")
    sig = pval < args.alpha
    print(f"  result             : {'SIGNIFICANT' if sig else 'not significant'} at alpha={args.alpha}")


def cmd_chisq(args):
    rows = []
    for pair in args.counts:
        a, b = pair.split(",")
        rows.append([float(a), float(b)])
    R = len(rows)
    col_tot = [sum(r[0] for r in rows), sum(r[1] for r in rows)]
    grand = sum(col_tot)
    chi = 0.0
    for r in rows:
        rt = r[0] + r[1]
        for j in (0, 1):
            exp = rt * col_tot[j] / grand
            if exp > 0:
                chi += (r[j] - exp) ** 2 / exp
    df = (R - 1) * (2 - 1)
    pval = chisq_sf(chi, df)
    print("Chi-square test of independence")
    print("-" * 42)
    for i, r in enumerate(rows):
        tot = r[0] + r[1]
        print(f"  variant {i}: {int(r[0]):,}/{int(tot):,} = {r[0]/tot:.4%}")
    print(f"  chi-square         : {chi:.4f}  (df {df})")
    print(f"  p-value            : {pval:.6f}")
    sig = pval < args.alpha
    print(f"  result             : {'SIGNIFICANT' if sig else 'not significant'} at alpha={args.alpha}")
    if sig:
        print("  next               : run pairwise prop tests with multiplicity correction")


def cmd_srm(args):
    obs = [float(x) for x in args.observed.split(",")]
    split = [float(x) for x in args.split.split(",")]
    if len(obs) != len(split):
        sys.exit("--observed and --split must have the same length")
    ssum = sum(split)
    split = [s / ssum for s in split]
    total = sum(obs)
    chi = sum((o - total * s) ** 2 / (total * s) for o, s in zip(obs, split))
    df = len(obs) - 1
    pval = chisq_sf(chi, df)
    print("Sample Ratio Mismatch (SRM) check")
    print("-" * 42)
    for i, (o, s) in enumerate(zip(obs, split)):
        print(f"  arm {i}: observed {int(o):,} ({o/total:.4%}) | expected {s:.4%}")
    print(f"  chi-square         : {chi:.4f}  (df {df})")
    print(f"  p-value            : {pval:.6f}")
    if pval < 0.001:
        print("  VERDICT            : SRM DETECTED (p<0.001) -- experiment is likely BROKEN.")
        print("                       Do NOT trust the results. Investigate assignment/logging.")
    else:
        print("  VERDICT            : no SRM detected; split looks healthy.")


def build_parser():
    p = argparse.ArgumentParser(description="A/B test design and analysis calculator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("size", help="required sample size per arm")
    s.add_argument("--baseline", type=float, required=True, help="baseline conversion rate (0-1)")
    s.add_argument("--mde-rel", type=float, help="minimum detectable effect, relative (e.g. 0.05 = +5%%)")
    s.add_argument("--mde-abs", type=float, help="minimum detectable effect, absolute (e.g. 0.005)")
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--power", type=float, default=0.80)
    s.add_argument("--one-sided", action="store_true")
    s.add_argument("--daily-per-arm", type=float, help="daily eligible traffic per arm (for duration estimate)")
    s.set_defaults(func=cmd_size)

    pr = sub.add_parser("prop", help="two-proportion z-test")
    pr.add_argument("--c-conv", type=int, required=True)
    pr.add_argument("--c-n", type=int, required=True)
    pr.add_argument("--t-conv", type=int, required=True)
    pr.add_argument("--t-n", type=int, required=True)
    pr.add_argument("--alpha", type=float, default=0.05)
    pr.set_defaults(func=cmd_prop)

    tt = sub.add_parser("ttest", help="Welch's t-test for means")
    tt.add_argument("--c-mean", type=float, required=True)
    tt.add_argument("--c-sd", type=float, required=True)
    tt.add_argument("--c-n", type=int, required=True)
    tt.add_argument("--t-mean", type=float, required=True)
    tt.add_argument("--t-sd", type=float, required=True)
    tt.add_argument("--t-n", type=int, required=True)
    tt.add_argument("--alpha", type=float, default=0.05)
    tt.set_defaults(func=cmd_ttest)

    cs = sub.add_parser("chisq", help="chi-square for >2 variant rates")
    cs.add_argument("--counts", nargs="+", required=True,
                    help="per-variant 'conv,nonconv' pairs, e.g. 100,900 130,870")
    cs.add_argument("--alpha", type=float, default=0.05)
    cs.set_defaults(func=cmd_chisq)

    sm = sub.add_parser("srm", help="sample ratio mismatch check")
    sm.add_argument("--observed", required=True, help="comma list of observed counts per arm")
    sm.add_argument("--split", required=True, help="comma list of planned split, e.g. 0.5,0.5")
    sm.set_defaults(func=cmd_srm)
    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
