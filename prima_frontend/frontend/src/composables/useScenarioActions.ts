import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { createScenarioService } from '@/services/scenarioService';
import type { MinimalDetailsScenario } from '../types/scenario';

export function useScenarioActions(callback?: any) {
    const scenarioService = createScenarioService();
    const authStore = useAuthStore();
    const router = useRouter();

    const scenarioIdBeingRenamed = ref<number | null>(null);
    const newScenarioName = ref('');
    const scenarioToBeCopied = ref<{ id: number } | null>(null);
    const scenarioCopyVisible = ref<boolean>(false);
    const scenarioRenameVisible = ref<boolean>(false);

    const handleScenarioRename = async () => {
        if (!scenarioIdBeingRenamed.value) return;

        try {
            await scenarioService.updateScenarioName(scenarioIdBeingRenamed.value, newScenarioName.value);
            callback?.();
            scenarioIdBeingRenamed.value = null;
            scenarioRenameVisible.value = false;
            newScenarioName.value = '';
        } catch (error) {
            console.error('Error renaming scenario:', error);
        }
    };

    const handleScenarioCopy = () => {
        router.push({
            path: '/create-scenario/use-cases',
            query: {
                copy: scenarioToBeCopied.value?.id
            }
        });
    };

    const handleCopyAndEditClick = (id: number) => {
        scenarioToBeCopied.value = { id };
        scenarioCopyVisible.value = true;
    };

    const handleRenameClick = (id: number) => {
        scenarioIdBeingRenamed.value = id;
        scenarioRenameVisible.value = true;
    };

    const canRenameScenario = (scenario: MinimalDetailsScenario) => {
        return (
            authStore.isSuperAdmin ||
            (authStore.isOrgAdmin && scenario?.organization?.id === authStore.user?.organizationId) ||
            scenario?.user?.id === authStore.user?.id
        );
    };

    return {
        scenarioIdBeingRenamed,
        newScenarioName,
        scenarioToBeCopied,
        handleScenarioRename,
        handleScenarioCopy,
        canRenameScenario,
        scenarioRenameVisible,
        scenarioCopyVisible,
        handleCopyAndEditClick,
        handleRenameClick
    };
}
