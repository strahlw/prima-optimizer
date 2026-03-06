export type LazyParams = {
    page: number;
    first: number;
    rows: number;
    sortField: string | null;
    sortOrder: number | null;
    addedDatasetWellIds?: number[];
    addedWellIds?: number[];
    wellType?: string[];
    taskId?: string | null;
};

export interface PaginationMeta {
    current_page: number;
    last_page: number;
    per_page: number;
    total: number;
    from: number;
    to: number;
}
