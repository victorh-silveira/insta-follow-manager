"""In-memory mock Instagram gateway for safe local development and testing."""

from src.domain.gateways.instagram_gateway import (
    AuthAccount,
    GatewayProfile,
    InstagramGateway,
)

_INITIAL_FOLLOWING: list[GatewayProfile] = [
    GatewayProfile(pk="101", username="ana.julia.dev", full_name="Ana Julia", is_verified=False),
    GatewayProfile(pk="102", username="artur_foto", full_name="Artur Mendes", is_verified=False),
    GatewayProfile(pk="103", username="andre.design", full_name="André Oliveira", is_verified=True),
    GatewayProfile(pk="104", username="agata.lima", full_name="Ágata Lima", is_verified=False),
    GatewayProfile(pk="105", username="bruno_tech", full_name="Bruno Almeida", is_verified=False),
    GatewayProfile(pk="106", username="bia.style", full_name="Beatriz Santos", is_verified=True),
    GatewayProfile(pk="107", username="carlos.fit", full_name="Carlos Eduardo", is_verified=False),
    GatewayProfile(pk="108", username="daniela_arq", full_name="Daniela Rocha", is_verified=False),
    GatewayProfile(pk="109", username="erika.m", full_name="Érika Martins", is_verified=False),
    GatewayProfile(pk="110", username="felipe_music", full_name="Felipe Nogueira", is_verified=False),
    GatewayProfile(pk="111", username="gabi.travel", full_name="Gabriela Teixeira", is_verified=True),
    GatewayProfile(pk="112", username="henrique.js", full_name="Henrique Barros", is_verified=False),
    GatewayProfile(pk="113", username="icaro_surf", full_name="Ícaro Ribeiro", is_verified=False),
    GatewayProfile(pk="114", username="julia.med", full_name="Julia Cardoso", is_verified=False),
    GatewayProfile(pk="115", username="lucas.code", full_name="Lucas Ferreira", is_verified=False),
    GatewayProfile(pk="116", username="mariana.art", full_name="Mariana Duarte", is_verified=True),
    GatewayProfile(pk="117", username="pedro.run", full_name="Pedro Henrique", is_verified=False),
    GatewayProfile(pk="118", username="rafael.ux", full_name="Rafael Moreira", is_verified=False),
    GatewayProfile(pk="119", username="sofia.books", full_name="Sofia Azevedo", is_verified=False),
    GatewayProfile(pk="120", username="tiago.chef", full_name="Tiago Barbosa", is_verified=False),
    GatewayProfile(pk="121", username="zeca.loja", full_name="Zeca Store", is_verified=False),
    GatewayProfile(pk="122", username="3dstudio.br", full_name="3D Studio Brasil", is_verified=False),
    GatewayProfile(pk="123", username="007tech", full_name="007 Tech News", is_verified=True),
    GatewayProfile(pk="124", username="lua_mistica", full_name="✨ Lua Mística", is_verified=False),
    GatewayProfile(pk="125", username="dev_anon", full_name="_dev_carlos", is_verified=False),
    GatewayProfile(pk="126", username="sem_nome_aqui", full_name="", is_verified=False),
]

_INITIAL_FOLLOWERS: list[GatewayProfile] = [
    GatewayProfile(pk="101", username="ana.julia.dev", full_name="Ana Julia", is_verified=False),
    GatewayProfile(pk="103", username="andre.design", full_name="André Oliveira", is_verified=True),
    GatewayProfile(pk="105", username="bruno_tech", full_name="Bruno Almeida", is_verified=False),
    GatewayProfile(pk="108", username="daniela_arq", full_name="Daniela Rocha", is_verified=False),
    GatewayProfile(pk="111", username="gabi.travel", full_name="Gabriela Teixeira", is_verified=True),
    GatewayProfile(pk="115", username="lucas.code", full_name="Lucas Ferreira", is_verified=False),
    GatewayProfile(pk="201", username="camila_f", full_name="Camila Vasconcelos", is_verified=False),
    GatewayProfile(pk="202", username="mateus.g", full_name="Mateus Gomes", is_verified=False),
    GatewayProfile(pk="203", username="99_freelas", full_name="99 Freelas", is_verified=False),
]


class MockInstagramGateway(InstagramGateway):
    """Stateful mock gateway that simulates Instagram following/followers & unfollow."""

    def __init__(self) -> None:
        self._following: dict[str, GatewayProfile] = {p.pk: p for p in _INITIAL_FOLLOWING}
        self._followers: dict[str, GatewayProfile] = {p.pk: p for p in _INITIAL_FOLLOWERS}
        self._authenticated = True
        self._username = "demo.manager"

    @property
    def mode_name(self) -> str:
        return "mock"

    def get_auth_status(self) -> AuthAccount:
        if not self._authenticated:
            return AuthAccount(is_authenticated=False)
        return AuthAccount(
            is_authenticated=True,
            username=self._username,
            full_name="Conta Demo",
        )

    def login(
        self,
        username: str,
        password: str,
        verification_code: str | None = None,
    ) -> AuthAccount:
        self._authenticated = True
        self._username = username
        return self.get_auth_status()

    def logout(self) -> None:
        self._authenticated = False

    def fetch_following(self) -> list[GatewayProfile]:
        return list(self._following.values())

    def fetch_followers(self) -> list[GatewayProfile]:
        return list(self._followers.values())

    def unfollow(self, pk: str) -> None:
        self._following.pop(pk, None)
