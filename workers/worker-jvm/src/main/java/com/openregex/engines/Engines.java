package com.openregex.engines;

import com.openregex.models.Models.EngineInfo;
import com.openregex.models.Models.WorkerInfo;
import java.util.List;

public class Engines {
    public static final List<EngineInfo> ENGINES_LIST = List.of(
            JvmStandard.ENGINE,
            JvmRe2j.ENGINE
    );

    public static final WorkerInfo WORKER_INFO = new WorkerInfo(
            "worker-jvm",
            Common.WORKER_VERSION,
            Common.WORKER_RELEASE_DATE,
            Common.WORKER_SCHEMA_VERSION,
            ENGINES_LIST
    );
}