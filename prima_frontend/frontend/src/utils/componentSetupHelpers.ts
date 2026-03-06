import { createFormService } from '@/services/formService';
import { createRankingService } from '@/services/rankingService';
import { createDownloadService } from '@/services/downloadService';
import { createWellOverviewService } from '@/services/wellOverviewService';
import { useRouter } from 'vue-router';

import { useScenarioFormStore } from '@/stores/form/scenarioForm';
import { useWellOverviewStore } from '@/stores/wellOverviewStore';
import { useRankingStore } from '@/stores/form/rankingStore';

export function setupWellRankingPage() {
    return {
        formService: createFormService(),
        rankingService: createRankingService(),
        downloadService: createDownloadService(),
        wellOverviewService: createWellOverviewService(),
        scenarioFormStore: useScenarioFormStore(),
        wellOverviewStore: useWellOverviewStore(),
        rankingStore: useRankingStore(),
        router: useRouter()
    };
}
