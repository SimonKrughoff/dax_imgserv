# This file is part of dax_imgserv.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

from flask import session

import lsst.afw.image as afw_image

from ..locateImage import get_image
from .dal import DAL
# use following format to prevent circular reference
import lsst.dax.imgserv.jobqueue.imageworker as imageworker

""" This module implements the IVOA's SODA v1.0 per LSST requirements.

    All ra,dec values are expressed in ICRS degrees, by default.

    Shape parameters:
        CIRCLE <ra> <dec> <radius>
        RANGE <ra1> <ra2> <dec1> <dec2>
        POLYGON <ra1> <dec1> ... (at least 3 pairs)
        BBOX <ra> <dec> <w> <h> <filter> <unit>

    The parameters are represented in `dict`, for example: 
        {'ID': 'DC_W13_Stripe82.calexp.r', 'CIRCLE 37.644598 0.104625 100'}
"""


class ImageSODA(DAL):
    """ Class to handle SODA operations.

    """
    def __init__(self, config):
        self._config = config

    def do_test(self, params: dict) -> afw_image:
        """ Do sync operation.

        Parameters
        ---------
        params : `dict`
            the request parameters (See Shape requirements above)

        Returns
        -------
        resp: `lsst.afw.image`
            the image object.
        """
        cutout = get_image(params, self._config)
        return cutout

    def do_sync(self, params: dict) -> afw_image:
        """ Do sync operation.

        Parameters
        ---------
        params : `dict`
            the request parameters (See Shape requirements above)

        Returns
        -------
        resp: `lsst.afw.image`
            the image object.
        """
        if "POS" in params:
            if "ID" not in params:
                database = 'default'
                dataset_id = 'default'
                band = 'default'
            else:
                database, dataset_id, band = params['ID'].split('.')
            cutout = get_image(database, dataset_id, params['POS'].split()[0], *params['POS'].split()[1:])
            return cutout
        else:
            raise NotImplementedError("ImageSODA.do_sync(): Unsupported "
                                      "Request")

    def do_async(self, params: dict) -> str:
        """ For async operation, create a new task for the request, enqueue for
        later processing, then return the task_id for tracking it.

        Parameters
        ----------
        params : `dict`
            the request parameters. (See Shape parameters above)

        Returns
        -------
        task.task_id: `str`
            the newly created task/job id.

        """
        user = session.get("user", "UNKNOWN")
        # enqueue the request for image_worker
        job_creation_time = datetime.timestamp(datetime.now())
        kwargs = {"job_creation_time": job_creation_time, "owner": user}
        task = imageworker.get_image_async.apply_async(
            queue="imageworker_queue",
            args=[params],
            kwargs=kwargs
        )
        return task.task_id

    def do_sia(self, params: dict) -> object:
        """ Do SIA operation.

        Parameters
        ----------
        params : `dict`
            the request parameters.

        Returns
        -------
        xml: `str`

        """
        raise NotImplementedError("ImageSODA.do_sia()")

    def get_examples(self, params:dict) -> str:
        """ Get examples for this service.

        Parameters
        ----------
        params : `dict`

        Returns
        -------
        xml: `str`

        """
        return super().get_examples(params)

    def get_tables(self, params:dict) -> str:
        """ Get examples for this service.

        Parameters
        ----------
        params : `dict`

        Returns
        -------
        xml: `str`

        """
        raise NotImplementedError("ImageSODA.get_tables()")

    def get_availability(self, params: dict) -> str:
        """ Get the service availability status.

        Parameters
        ---------
        params : `dict`

        Returns
        -------
        xml: `str`

        """
        params["status"] = "true"  # xsd:boolean type
        params["service_name"] = "Image SODA"
        return super().get_availability(params)

    def get_capabilities(self, params: dict) -> str:
        """ Get the service capabilities.

        Parameters
        ----------
        params : `dict`
            the HTTP parameters.

        Returns
        -------
        xml: `str`

        """
        return super().get_capabilities(params)

