import os
import threading
from typing import Any
from time import time, sleep
from swagger_server.database.enums.edition_status import EditionStatus
from swagger_server.database.models.edition import EditionModel
from swagger_server.decorators import logger
from swagger_server.exceptions import TimeoutException
from swagger_server.graphql_schemas.queries import SearchEditionsQuery
from swagger_server.__main__ import flask_app, db

ZERO_VALUE = 0
POLLING_INTERVAL = float(os.environ.get("POLLING_INTERVAL"))
TIMEOUT = 900  # Ethereum 15 minutes timeout


class PublishEditionThread:
    __minting_service: Any
    __editions_service: Any

    def __init__(self, minting_service, editions_service):
        self.__minting_service = minting_service
        self.__editions_service = editions_service

    def get_dapper_edition_id(self, flow_id: int) -> str:
        query = SearchEditionsQuery([flow_id])
        result: dict = self.__minting_service.query(query)
        result_value: dict = result["data"][query.mutation_name]
        if result_value["count"] > ZERO_VALUE:
            return result_value["editions"][ZERO_VALUE]["id"]
        else:
            return None

    @logger()
    def query_polling_edition_id(self, flow_id: int, edition_id: int) -> str:
        start_time = time()
        dapper_edition_id: str = None
        while not dapper_edition_id:
            if time() - start_time > TIMEOUT:
                self.__editions_service.create_error(
                    edition_id=edition_id,
                    error=f"Timeout creating the Edition in blockchain.",
                    type="Timeout",
                    suggested_solution="Try to publish the Edition again.",
                )
                self.__editions_service.update_edition(
                    edition_id,
                    EditionModel(
                        status=EditionStatus.ERROR,
                    ),
                )
                db.session.commit()
                raise TimeoutException(
                    title="Timeout creating the Edition in blockchain"
                )
            sleep(POLLING_INTERVAL)
            dapper_edition_id = self.get_dapper_edition_id(flow_id)
        return dapper_edition_id

    @logger()
    def get_dapper_edition_id_and_update_edition(self, edition_id: int, flow_id: int):
        with flask_app.app_context():
            edition = self.__editions_service.get_edition(edition_id)
            dapper_edition_id = self.query_polling_edition_id(flow_id, edition_id)
            self.__editions_service.update_edition(
                edition.id,
                EditionModel(
                    status=EditionStatus.CREATED,
                    dapper_edition_id=dapper_edition_id,
                ),
            )
            self.__minting_service.update_edition(dapper_edition_id, edition)
            db.session.commit()

    def start(self, edition_id: int, flow_id: int):
        """Creates a new thread to poll the dapper API until the Edition is created to get its id.
        Then updates the edition status and dapper_edition_id.
        Finally performs the UpdateEdition to set the metadata in Dapper's DB.

        :param edition_id: int
        :param flow_id: int
        """
        thread = threading.Thread(
            target=self.get_dapper_edition_id_and_update_edition,
            args=(edition_id, flow_id),
        )
        thread.setDaemon(True)
        thread.start()
