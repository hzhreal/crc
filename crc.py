from nat import Nat
from gf2x import GF2x, GF2x_MOD_f
from typing import Final

if 0:
    def calc_crc(data: bytes | bytearray, generator: GF2x) -> int:
        # The CRC of a message polynomial $M(x)$ is defined as the remainder $R(x)$
        # obtained by dividing $M(x) * x^n$ by a generator polynomial of degree $n$.
        # A message can be many bits in length, storing it as one polynomial is not ideal.
        # We only need the remainder.
        # Note that $(M(x) * x^n) + (G(x)) = R(x) + (G(x))$ in $(GF(2)[x])/(G(x))$.

        # Let $M(x)$ be a sequence of $m$ bytes, recall that a byte is defined as 8 bits.
        # That is, $M(x) = M_0(x) * x^{8(m-1)} + M_1(x) * x^{8(m-2)} + \cdots + M_{m-2}(x) * x^8 + M_{m-1}(x)$,
        # where each $M_i(x)$ is a polynomial representing a single byte.
        # These polynomials are which we will process one by one, in the order $(M_0(x), \ldots, M_{m-1}(x))$.
        # Indeed. Let $R_0(x) = 0$, define $R_1(x) = R_0(x) * x^8 + M_0(x) * x^n$.
        # If $R_i(x) = R_{i-1}(x) * x^8 + M_{i-1}(x) * x^n$, then define $R_{i+1} = R_i(x) * x^8 + M_i(x) * x^n$.

        # It follows that:
        # $R_0(x) + (G(x)) = 0$
        # $R_1(x) + (G(x)) = M_0(x) + (G(x))$
        # $R_2(x) + (G(x)) = (M_0(x) * x^8 + M_1(x) * x^n) + (G(x))$
        # $\vdots$
        # $R_m(x) + (G(x)) = (M(x) * x^n) + (G(x))$.

        r = GF2x_MOD_f(generator, GF2x(Nat(0)))

        for b in data:
            r = r * GF2x_MOD_f(generator, GF2x.generate_monomial(Nat(8))) + \
                GF2x_MOD_f(generator, GF2x(Nat(b)) * GF2x.generate_monomial(Nat(generator.degree)))

        return int(r.repr.repr)

class CRC:
    def __init__(
        self,
        width: int,
        poly: int,
        init: int,
        ref_in: bool,
        ref_out: bool,
        xor_out: int,
        check: int | None = None,
        data: bytes | bytearray | None = None
    ) -> None:
        self.width:   Final[Nat]  = Nat(width)
        assert width != Nat(0)
        self.poly:    Final[GF2x] = GF2x((Nat(1) << self.width) | Nat(poly))
        assert self.poly.degree == self.width

        self.init:    Final[GF2x] = GF2x(Nat(init))
        self.ref_in:  Final[bool] = ref_in
        self.ref_out: Final[bool] = ref_out
        self.xor_out: Final[Nat]  = Nat(xor_out)

        self._crc: GF2x_MOD_f = GF2x_MOD_f(self.poly, self.init)

        if check is not None:
            self.update(b"123456789")
            assert self.digest() == check
            self.reset()

        if data is not None:
            self.update(data)

    @staticmethod
    def _reflect(n: Nat, l: Nat) -> Nat:
        ref = Nat(0)
        for i in range(int(l)):
            pos = (l - Nat(1)) - Nat(i)
            bit = Nat(1) & n
            ref = ref | (bit << pos)
            n = n >> Nat(1)
        return ref

    def reset(self) -> None:
        self._crc = GF2x_MOD_f(self.poly, self.init)

    def update(self, data: bytes | bytearray) -> None:
        for b in data:
            b = Nat(b)
            if self.ref_in:
                b = self._reflect(b, Nat(8))
            self._crc = self._crc * GF2x_MOD_f(self.poly, GF2x.generate_monomial(Nat(8))) + \
                        GF2x_MOD_f(self.poly, GF2x(b) * GF2x.generate_monomial(self.width))

    def digest(self) -> int:
        if self.ref_out:
            n = self._reflect(self._crc.repr.repr, self.width)
        else:
            n = self._crc.repr.repr
        n = n ^ self.xor_out
        return int(n)

