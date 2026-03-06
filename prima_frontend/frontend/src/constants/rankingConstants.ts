export interface ColumnDefinition {
    key: string;
    field: string;
    header: string;
    score?: boolean;
    factor?: string;
}

export const columns: ColumnDefinition[] = [
    { key: 'wellRank', field: 'json.wellRank', header: 'Well Rank' },
    { key: 'wellId', field: 'json.wellId', header: 'Well ID' },
    // { key: 'operatorName', field: 'json.operatorName', header: 'Operator Name' },
    { key: 'wellName', field: 'json.wellName', header: 'Well Name' },
    { key: 'wellType', field: 'json.wellType', header: 'Well Type' },
    { key: 'wellAgeScore', field: 'wellAgeScore', header: 'Well Age Score', score: true, factor: 'wellAge' },
    {
        key: 'ownerWellCountScore',
        field: 'ownerWellCountScore',
        header: 'Owner Well-Count',
        score: true,
        factor: 'ownerWellCount'
    },
    {
        key: 'lifeOilProductionScore',
        field: 'lifeOilProductionScore',
        header: 'Lifetime Production Volume - Oil Score',
        score: true,
        factor: 'lifelongProductionVolume.childFactors.lifelongOilProduction'
    },
    {
        key: 'lifeGasProductionScore',
        field: 'lifeGasProductionScore',
        header: 'Lifetime Production Volume - Gas Score',
        score: true,
        factor: 'lifelongProductionVolume.childFactors.lifelongGasProduction'
    },
    {
        key: 'annGasProductionScore',
        field: 'annGasProductionScore',
        header: 'Annual Production Volume - Gas Score',
        score: true,
        factor: 'annProductionVolume.childFactors.annGasProduction'
    },
    {
        key: 'annOilProductionScore',
        field: 'annOilProductionScore',
        header: 'Annual Production Volume - Oil Score',
        score: true,
        factor: 'annProductionVolume.childFactors.annOilProduction'
    },
    {
        key: 'fiveYearGasProductionScore',
        field: 'fiveYearGasProductionScore',
        header: '5-Year Production Volume - Gas Score',
        score: true,
        factor: 'fiveYearProductionVolume.childFactors.fiveYearGasProduction'
    },
    {
        key: 'fiveYearOilProductionScore',
        field: 'fiveYearOilProductionScore',
        header: '5-Year Production Volume - Oil Score',
        score: true,
        factor: 'fiveYearProductionVolume.childFactors.fiveYearOilProduction'
    },
    {
        key: 'schoolsScore',
        field: 'schoolsScore',
        header: 'Sensitive Receptors - Schools Score',
        score: true,
        factor: 'sensitiveReceptors.childFactors.schools'
    },
    {
        key: 'hospitalsScore',
        field: 'hospitalsScore',
        header: 'Sensitive Receptors - Hospitals Score',
        score: true,
        factor: 'sensitiveReceptors.childFactors.hospitals'
    },
    {
        key: 'agricultureAreaNearbyScore',
        field: 'agricultureAreaNearbyScore',
        header: 'Sensitive Receptors - Agriculture Area Nearby Score',
        score: true,
        factor: 'sensitiveReceptors.childFactors.agricultureAreaNearby'
    },
    {
        key: 'buildingsNearScore',
        field: 'buildingsNearScore',
        header: 'Sensitive Receptors - Buildings (Near) Score',
        score: true,
        factor: 'sensitiveReceptors.childFactors.buildingsNear'
    },
    {
        key: 'buildingsFarScore',
        field: 'buildingsFarScore',
        header: 'Sensitive Receptors - Buildings (Far) Score',
        score: true,
        factor: 'sensitiveReceptors.childFactors.buildingsFar'
    },
    {
        key: 'endangeredSpeciesOnSiteScore',
        field: 'endangeredSpeciesOnSiteScore',
        header: 'Ecological Receptors - Endangered Species on Site Score',
        score: true,
        factor: 'ecologicalReceptors.childFactors.endangeredSpeciesOnSite'
    },
    {
        key: 'waterSourceNearbyScore',
        field: 'waterSourceNearbyScore',
        header: 'Environment - Water Source Nearby Score',
        score: true,
        factor: 'environment.childFactors.waterSourceNearby'
    },
    {
        key: 'knownSoilOrWaterImpactScore',
        field: 'knownSoilOrWaterImpactScore',
        header: 'Environment - Known Soil or Water Impact Score',
        score: true,
        factor: 'environment.childFactors.knownSoilOrWaterImpact'
    },
    {
        key: 'fedWetlandsNearScore',
        field: 'fedWetlandsNearScore',
        header: 'Environment - Federal Wetlands (Near) Score',
        score: true,
        factor: 'environment.childFactors.fedWetlandsNear'
    },
    {
        key: 'fedWetlandsFarScore',
        field: 'fedWetlandsFarScore',
        header: 'Environment - Federal Wetlands (Far) Score',
        score: true,
        factor: 'environment.childFactors.fedWetlandsFar'
    },
    {
        key: 'stateWetlandsNearScore',
        field: 'stateWetlandsNearScore',
        header: 'Environment - State Wetlands (Near) Score',
        score: true,
        factor: 'environment.childFactors.stateWetlandsNear'
    },
    {
        key: 'stateWetlandsFarScore',
        field: 'stateWetlandsFarScore',
        header: 'Environment - State Wetlands (Far) Score',
        score: true,
        factor: 'environment.childFactors.stateWetlandsFar'
    },
    {
        key: 'historicalPreservationSiteScore',
        field: 'historicalPreservationSiteScore',
        header: 'Site Considerations - Historical Preservation Site Score',
        score: true,
        factor: 'siteConsiderations.childFactors.historicalPreservationSite'
    },
    {
        key: 'homeUseGasWellScore',
        field: 'homeUseGasWellScore',
        header: 'Site Considerations - Home Use Gas Well Score',
        score: true,
        factor: 'siteConsiderations.childFactors.homeUseGasWell'
    },
    {
        key: 'postPluggingLandUseScore',
        field: 'postPluggingLandUseScore',
        header: 'Site Considerations - Post-Plugging Land Use Score',
        score: true,
        factor: 'siteConsiderations.childFactors.postPluggingLandUse'
    },
    {
        key: 'surfaceEquipmentOnSiteScore',
        field: 'surfaceEquipmentOnSiteScore',
        header: 'Site Considerations - Surface Equipment On Site Score',
        score: true,
        factor: 'siteConsiderations.childFactors.surfaceEquipmentOnSite'
    },
    {
        key: 'likelyToBeOrphanedScore',
        field: 'likelyToBeOrphanedScore',
        header: 'Likely to be Orphaned Score',
        score: true,
        factor: 'likelyToBeOrphaned'
    },
    {
        key: 'inTribalLandScore',
        field: 'inTribalLandScore',
        header: 'In Tribal Land Score',
        score: true,
        factor: 'inTribalLand'
    },
    {
        key: 'costOfPluggingScore',
        field: 'costOfPluggingScore',
        header: 'Cost Of Plugging Score',
        score: true,
        factor: 'costOfPlugging'
    },
    {
        key: 'highPressureObservedScore',
        field: 'highPressureObservedScore',
        header: 'High Pressure Observed Score',
        score: true,
        factor: 'highPressureObserved'
    },
    {
        key: 'idleStatusDurationScore',
        field: 'idleStatusDurationScore',
        header: 'Idle Status Duration Score',
        score: true,
        factor: 'idleStatusDuration'
    },
    {
        key: 'numberOfMcwsNearbyScore',
        field: 'numberOfMcwsNearbyScore',
        header: 'Number Of MCWs Nearby Score',
        score: true,
        factor: 'numberOfMcwsNearby'
    },
    {
        key: 'mechanicalIntegrityTestScore',
        field: 'mechanicalIntegrityTestScore',
        header: 'Mechanical Integrity Test Score',
        score: true,
        factor: 'mechanicalIntegrityTest'
    },
    {
        key: 'otherwiseIncentivizedWellScore',
        field: 'otherwiseIncentivizedWellScore',
        header: 'Otherwise Incentivized Well Score',
        score: true,
        factor: 'otherwiseIncentivizedWell'
    },
    {
        key: 'wellIntegrityScore',
        field: 'wellIntegrityScore',
        header: 'Well Integrity Score',
        score: true,
        factor: 'wellIntegrity'
    },
    {
        key: 'placeholderOneScore',
        field: 'placeholderOneScore',
        header: 'Placeholder 1 Score',
        score: true,
        factor: 'placeholderOne'
    },
    {
        key: 'placeholderTwoScore',
        field: 'placeholderTwoScore',
        header: 'Placeholder 2 Score',
        score: true,
        factor: 'placeholderTwo'
    },
    {
        key: 'placeholderThreeScore',
        field: 'placeholderThreeScore',
        header: 'Placeholder 3 Score',
        score: true,
        factor: 'placeholderThree'
    },
    {
        key: 'placeholderFourScore',
        field: 'placeholderFourScore',
        header: 'Placeholder 4 Score',
        score: true,
        factor: 'placeholderFour'
    },
    {
        key: 'placeholderFiveScore',
        field: 'placeholderFiveScore',
        header: 'Placeholder 5 Score',
        score: true,
        factor: 'placeholderFive'
    },
    {
        key: 'placeholderSixScore',
        field: 'placeholderSixScore',
        header: 'Placeholder 6 Score',
        score: true,
        factor: 'placeholderSix'
    },
    {
        key: 'placeholderSevenScore',
        field: 'placeholderSevenScore',
        header: 'Placeholder 7 Score',
        score: true,
        factor: 'placeholderSeven'
    },
    {
        key: 'placeholderEightScore',
        field: 'placeholderEightScore',
        header: 'Placeholder 8 Score',
        score: true,
        factor: 'placeholderEight'
    },
    {
        key: 'placeholderNineScore',
        field: 'placeholderNineScore',
        header: 'Placeholder 9 Score',
        score: true,
        factor: 'placeholderNine'
    },
    {
        key: 'placeholderTenScore',
        field: 'placeholderTenScore',
        header: 'Placeholder 10 Score',
        score: true,
        factor: 'placeholderTen'
    },
    {
        key: 'placeholderElevenScore',
        field: 'placeholderElevenScore',
        header: 'Placeholder 11 Score',
        score: true,
        factor: 'placeholderEleven'
    },
    {
        key: 'placeholderTwelveScore',
        field: 'placeholderTwelveScore',
        header: 'Placeholder 12 Score',
        score: true,
        factor: 'placeholderTwelve'
    },
    {
        key: 'placeholderThirteenScore',
        field: 'placeholderThirteenScore',
        header: 'Placeholder 13 Score',
        score: true,
        factor: 'placeholderThirteen'
    },
    {
        key: 'placeholderFourteenScore',
        field: 'placeholderFourteenScore',
        header: 'Placeholder 14 Score',
        score: true,
        factor: 'placeholderFourteen'
    },
    {
        key: 'placeholderFifteenScore',
        field: 'placeholderFifteenScore',
        header: 'Placeholder 15 Score',
        score: true,
        factor: 'placeholderFifteen'
    },
    {
        key: 'placeholderSixteenScore',
        field: 'placeholderSixteenScore',
        header: 'Placeholder 16 Score',
        score: true,
        factor: 'placeholderSixteen'
    },
    {
        key: 'placeholderSeventeenScore',
        field: 'placeholderSeventeenScore',
        header: 'Placeholder 17 Score',
        score: true,
        factor: 'placeholderSeventeen'
    },
    {
        key: 'placeholderEighteenScore',
        field: 'placeholderEighteenScore',
        header: 'Placeholder 18 Score',
        score: true,
        factor: 'placeholderEighteen'
    },
    {
        key: 'placeholderNineteenScore',
        field: 'placeholderNineteenScore',
        header: 'Placeholder 19 Score',
        score: true,
        factor: 'placeholderNineteen'
    },
    {
        key: 'placeholderTwentyScore',
        field: 'placeholderTwentyScore',
        header: 'Placeholder 20 Score',
        score: true,
        factor: 'placeholderTwenty'
    },
    {
        key: 'leakScore',
        field: 'json.leakScore',
        header: 'Losses - Leak Score',
        score: true,
        factor: 'losses.childFactors.leak'
    },
    {
        key: 'complianceScore',
        field: 'complianceScore',
        header: 'Losses - Compliance Score',
        score: true,
        factor: 'losses.childFactors.leak'
    },
    {
        key: 'incidentScore',
        field: 'incidentScore',
        header: 'Losses - Incident Score',
        score: true,
        factor: 'losses.childFactors.incident'
    },
    {
        key: 'hydrocarbonLossesScore',
        field: 'hydrocarbonLossesScore',
        header: 'Losses - Hydrocarbon Losses Score',
        score: true,
        factor: 'losses.childFactors.hydrocarbonLosses'
    },
    {
        key: 'violationScore',
        field: 'violationScore',
        header: 'Losses - Violation Score',
        score: true,
        factor: 'losses.childFactors.violation'
    },
    {
        key: 'brineLeakScore',
        field: 'brineLeakScore',
        header: 'Other Losses - Brine Leak Score',
        score: true,
        factor: 'otherLosses.childFactors.brineLeak'
    },
    {
        key: 'h2sLeakScore',
        field: 'h2sLeakScore',
        header: 'Other Losses - H2S Leak Score',
        score: true,
        factor: 'otherLosses.childFactors.h2sLeak'
    },
    { key: 'priorityScore', field: 'priorityScore', header: 'Priority Score [0-100]', score: true }
    // { key: 'name', field: 'json.well_name', header: 'Name' },
    // { key: 'age', field: 'json.age', header: 'Age [Years]' },
    // { key: 'depth', field: 'json.depth', header: 'Depth [ft]' },
    // { key: 'oil', field: 'json.oil', header: 'Oil [bbl/Year]' },
    // { key: 'gas', field: 'json.gas', header: 'Gas [Mcf/Year]' },
    // { key: '5YearOilProduction', field: 'json.5YearOilProduction', header: '5-Year Oil Production [bbl]' },
    // { key: '5YearGasProduction', field: 'json.5YearGasProduction', header: '5-Year Gas Production [Mcf]' },
    // { key: 'latitude', field: 'json.latitude', header: 'Latitude' },
    // { key: 'longitude', field: 'json.longitude', header: 'Longitude' },

    // { key: 'censusTractId', field: 'json.censusTractId', header: 'Census Tract ID' },
    // { key: 'stateCode', field: 'json.stateCode', header: 'State Code' },
    // { key: 'countyCode', field: 'json.countyCode', header: 'County Code' },
    // { key: 'landArea', field: 'json.landArea', header: 'Land Area' },
    // { key: 'h2sLeak', field: 'json.h2sLeak', header: 'H2S Leak' },
    // { key: 'lifelongOilProduction', field: 'json.lifelongOilProduction', header: 'Lifelong Oil Production [bbl]' },
    // { key: 'lifelongGasProduction', field: 'json.lifelongGasProduction', header: 'Lifelong Gas Production [Mcf]' },
    // { key: 'leak', field: 'json.leak', header: 'Leak' },
    // { key: 'elevationDelta', field: 'json.elevationDelta', header: 'Elevation Delta [m]' },
    // { key: 'distanceToRoad', field: 'json.distanceToRoad', header: 'Distance to Road [miles]' },
    // { key: 'leakFlag', field: 'json.leakFlag', header: 'Leak Flag' }
];
