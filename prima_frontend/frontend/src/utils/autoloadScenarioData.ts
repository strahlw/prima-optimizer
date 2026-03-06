// Local testing utility to copy and paste scenario data, then auto add it to the form
import { toCamelCase } from '@/utils/toCamelCase';

export async function autoloadScenarioData(scenarioFormStore: any) {
    if (import.meta.env.VITE_APP_ENV === 'local') {
        // const { autoloadData } = await import('@/data/mock/autoloadScenario');
        // if (!autoloadData) return;
        // Object.entries(autoloadData.general_specifications).forEach(([key, value]) => {
        //     const camelCaseKey = toCamelCase(key);
        //     if (camelCaseKey === 'organization' || camelCaseKey === 'datasetId') return;
        //     if (camelCaseKey in scenarioFormStore.form.generalSpecifications.basic) {
        //         (scenarioFormStore.form.generalSpecifications.basic as any)[camelCaseKey] = value;
        //     } else if (camelCaseKey in scenarioFormStore.form.generalSpecifications.plugging) {
        //         (scenarioFormStore.form.generalSpecifications.plugging as any)[camelCaseKey] = value;
        //     } else if (camelCaseKey in scenarioFormStore.form.generalSpecifications.dataQuality) {
        //         (scenarioFormStore.form.generalSpecifications.dataQuality as any)[camelCaseKey] = value;
        //     } else if (camelCaseKey in scenarioFormStore.form.generalSpecifications.solver) {
        //         (scenarioFormStore.form.generalSpecifications.solver as any)[camelCaseKey] = value;
        //     }
        // });
        // Object.entries(autoloadData.impact_factors).forEach(([key, value]) => {
        //     const camelCaseKey = toCamelCase(key);
        //     if (camelCaseKey in scenarioFormStore.form.impactFactors) {
        //         if ((value as any).child_factors) {
        //             Object.entries((value as any).child_factors).forEach(([childKey, childValue]) => {
        //                 const camelCaseChildKey = toCamelCase(childKey);
        //                 if (
        //                     camelCaseChildKey in
        //                     (scenarioFormStore.form.impactFactors as any)[camelCaseKey].childFactors
        //                 ) {
        //                     ((scenarioFormStore.form.impactFactors as any)[camelCaseKey].childFactors as any)[
        //                         camelCaseChildKey
        //                     ] = {
        //                         ...(typeof childValue === 'object' && childValue !== null ? childValue : {}),
        //                         toolTip: (scenarioFormStore.form.impactFactors as any)[camelCaseKey].childFactors[
        //                             camelCaseChildKey
        //                         ].toolTip
        //                     };
        //                 }
        //             });
        //             (scenarioFormStore.form.impactFactors as any)[camelCaseKey] = {
        //                 ...(typeof value === 'object' && value !== null ? value : {}),
        //                 childFactors: (scenarioFormStore.form.impactFactors as any)[camelCaseKey].childFactors,
        //                 toolTip: (scenarioFormStore.form.impactFactors as any)[camelCaseKey].toolTip
        //             };
        //         } else {
        //             (scenarioFormStore.form.impactFactors as any)[camelCaseKey] = {
        //                 ...(typeof value === 'object' && value !== null ? value : {}),
        //                 toolTip: (scenarioFormStore.form.impactFactors as any)[camelCaseKey].toolTip
        //             };
        //         }
        //     }
        // });
        // Object.entries(autoloadData.efficiency_factors).forEach(([key, value]) => {
        //     const camelCaseKey = toCamelCase(key);
        //     if (camelCaseKey in scenarioFormStore.form.efficiencyFactors) {
        //         (scenarioFormStore.form.efficiencyFactors as any)[camelCaseKey] = {
        //             ...(typeof value === 'object' && value !== null ? value : {}),
        //             toolTip: (scenarioFormStore.form.efficiencyFactors as any)[camelCaseKey].toolTip
        //         };
        //     }
        // });
    }
}
