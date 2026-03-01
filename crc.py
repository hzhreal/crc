from nat import Nat
from gf2x import GF2x, GF2x_MOD_f

def calc_crc(data: bytes | bytearray, generator: GF2x) -> int:
    # The CRC of a message polynomial $M(x)$ is defined as the remainder $R(x)$
    # obtained by dividing $M(x) * x^n$ by a generator polynomial of degree $n$.
    # A message can be many bits in length, storing it as one polynomial is not ideal.
    # We only need the remainder.
    # Note that $(M(x) * x^n) + (G(x)) = R(x) + (G(x))$ in $(GF(2)[x])/(G(x))$.

    # Let $M(x)$ be a sequence of $m$ bytes, recall a byte is defined as 8 bits.
    # That is, $M(x) = M_0(x) + M_1(x) * x^7 + ... + M_{m-1}(x) * x^{8(m-1) - 1}$,
    # where each $M_i(x)$ is a polynomial representing a single byte, these polynomials are which we will process one by one.
    # Indeed. Let $R_0(x) = 0$, define $R_1(x) = R_0(x) * x^8 + M_0(x) * x^n$.
    # If $R_i(x) = R_{i-1}(x) * x^8 + M_{i-1}(x) * x^n$, then define $R_{i+1} = R_i(x) * x^8 + M_i(x) * x^n$.

    # It follows that:
    # $R_0(x) + (G(x)) = 0$
    # $R_1(x) + (G(x)) = M_0(x) + (G(x))$
    # $R_2(x) + (G(x)) = (M_0(x) * x^8 + M_1(x) * x^n) + (G(x))
    # .
    # .
    # .
    # $R_{m} + (G(x)) = (M(x) * x^n) + (G(x))$.

    r = GF2x_MOD_f(generator, GF2x(Nat(0)))

    for b in data:
        r = r * GF2x_MOD_f(generator, GF2x.generate_monomial(Nat(8))) + \
            GF2x_MOD_f(generator, GF2x(Nat(b)) * GF2x.generate_monomial(Nat(generator.degree)))

    return int(r.repr.repr)

def test() -> None:
    import anycrc
    from os import urandom as rand

    SAMPLE_SIZE = 256
    SAMPLES     = 100
    GENERATOR = 0b100000100110000010001110110110111
    for i in range(1, SAMPLES + 1, 1):
        print(f"{i}/{SAMPLES}")

        data = rand(SAMPLE_SIZE)
        internal = calc_crc(data, GF2x(Nat(GENERATOR)))
        external = anycrc.CRC(width=32, poly=GENERATOR, init=0, refin=False, refout=False, xorout=0).calc(data)
        assert internal == external

if __name__ == "__main__":
    test()
