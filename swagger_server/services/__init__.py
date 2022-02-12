import os
from swagger_server.services.data_definitions_service import DataDefinitionsService
from swagger_server.services.minting_service import MintingService
from swagger_server.services.nft_service import NftService
from swagger_server.services.drops_service import DropsService
from swagger_server.services.drop_editions_service import DropEditionsService
from swagger_server.services.cms_service import CmsService
from swagger_server.services.scheduler_service import SchedulerService
from swagger_server.services.series_service import SeriesService
from swagger_server.services.collections_service import CollectionsService
from swagger_server.services.auth_service import AuthService
from swagger_server.services.editions_service import EditionsService
from swagger_server.mocks import (
    AuthServiceMock,
    CmsServiceMock,
    MintingServiceMock,
    DataDefinitionsServiceMock,
)

test_flag = os.getenv("TEST", "False").lower() in ("true", "1", "t")

auth = None

scheduler_service = SchedulerService()
if test_flag:
    data_definition_service = DataDefinitionsServiceMock()
    cms_service = CmsServiceMock()
    auth = AuthServiceMock(cms_service)
    minting_service = MintingServiceMock(cms_service)
else:
    data_definition_service = DataDefinitionsService()
    cms_service = CmsService()
    auth = AuthService(cms_service)
    minting_service = MintingService(cms_service)

nft_service = NftService()
series_service = SeriesService(minting_service, scheduler_service)
collections_service = CollectionsService(
    series_service, minting_service, scheduler_service
)
editions_service = EditionsService(
    cms_service,
    collections_service,
    series_service,
    minting_service,
    nft_service,
    data_definition_service,
    scheduler_service,
)
drop_editions_service = DropEditionsService(editions_service)
drops_service = DropsService(drop_editions_service, minting_service, scheduler_service)

minting_service.set_series_service(series_service)
minting_service.set_editions_service(editions_service)
series_service.set_collections_service(collections_service)
series_service.set_editions_service(editions_service)
collections_service.set_editions_service(editions_service)
