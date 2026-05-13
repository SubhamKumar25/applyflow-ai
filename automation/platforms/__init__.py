from automation.platforms.base import BasePlatformAdapter
from automation.platforms.linkedin import LinkedInAdapter
from automation.platforms.indeed import IndeedAdapter
from automation.platforms.naukri import NaukriAdapter
from automation.platforms.internshala import InternshalaAdapter
from automation.platforms.wellfound import WellfoundAdapter
from automation.platforms.foundit import FounditAdapter

ADAPTERS: dict[str, type[BasePlatformAdapter]] = {
    "linkedin": LinkedInAdapter,
    "indeed": IndeedAdapter,
    "naukri": NaukriAdapter,
    "internshala": InternshalaAdapter,
    "wellfound": WellfoundAdapter,
    "foundit": FounditAdapter,
}


def get_adapter(platform: str) -> BasePlatformAdapter:
    cls = ADAPTERS.get(platform.lower())
    if cls is None:
        raise ValueError(f"Unsupported platform: {platform}")
    return cls()


__all__ = ["BasePlatformAdapter", "ADAPTERS", "get_adapter"]
