import { useScenarioFormStore } from '../stores/form/scenarioForm';
import { useRouter } from 'vue-router';

export function useCreateScenario() {
    const scenarioFormStore = useScenarioFormStore();
    const router = useRouter();

    function createScenarioNavigation() {
        scenarioFormStore.resetForm();
        router.push('/create-scenario/use-cases');
    }

    return { createScenarioNavigation };
}
