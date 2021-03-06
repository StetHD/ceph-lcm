# -*- coding: utf-8 -*-
# Copyright (c) 2017 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Check that Ceph command is installed from the same repository."""


from decapod_admin.cluster_checks import base
from decapod_common import log


LOG = log.getLogger(__name__)
"""Logger."""


class Check(base.Check):

    async def run(self):
        query_result = await self.execute_cmd(
            "dpkg-query --showformat='${Version}' --show ceph-common",
            *self.cluster.server_list)

        self.manage_errors(
            "Cannot execute dpkg-query command on %s (%s): %s",
            "Not all hosts have installed ceph-common",
            query_result.errors
        )

        results = get_query_results(query_result.ok)
        query_lines = {line for _, line in results}
        if len(query_lines) >= 2:
            majority = self.get_majority(query_lines)
            for srv, line in results:
                if line != majority:
                    LOG.error(
                        (
                            "Server %s (%s) has ceph-common installed "
                            "with %s, majority is %s"
                        ),
                        srv.ip, srv.model_id, line, majority
                    )

            raise ValueError("Inconsistency in repo sources")


def get_query_results(results):
    return [(res.srv, res.stdout_text.strip()) for res in results]
