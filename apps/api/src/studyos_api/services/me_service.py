"""Business logic for identity-related use cases."""

from studyos_api.schemas.me import MePayload, PublicUser
from studyos_api.types.principal import User


class MeService:
    def build_me_payload(self, user: User | None) -> MePayload:
        if user is None:
            return MePayload(authenticated=False, user=None)
        return MePayload(
            authenticated=True,
            user=PublicUser(sub=user["sub"], roles=list(user["roles"])),
        )
