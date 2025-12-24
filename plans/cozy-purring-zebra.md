# AG-Grid 表格组件添加命令式 Ref API

## 需求

为 `AgGridTable` 组件添加从外部设置完整表格状态的能力，采用命令式 ref 设计。

## 设计方案

### 1. 类型定义

```typescript
// 暴露给外部的 ref 句柄类型
export interface AgGridTableRef<TData = unknown> {
  /** 设置表格状态（列状态 + 排序 + 筛选） */
  setState: (state: TableState) => void;

  /** 获取当前表格状态 */
  getState: () => TableState;

  /** 重置为默认状态（清除列宽/排序/筛选自定义） */
  resetState: () => void;

  /** 自动调整所有列宽 */
  sizeColumnsToFit: () => void;

  /** 获取原生 GridApi（高级用法） */
  getGridApi: () => GridApi<TData> | null;
}
```

### 2. 实现步骤

#### 步骤 1: 将组件改为 forwardRef

```typescript
// 之前
export function AgGridTable<TData = unknown>(props: AgGridTableProps<TData>) { ... }

// 之后
function AgGridTableInner<TData = unknown>(
  props: AgGridTableProps<TData>,
  ref: React.ForwardedRef<AgGridTableRef<TData>>
) { ... }

export const AgGridTable = React.forwardRef(AgGridTableInner) as <TData = unknown>(
  props: AgGridTableProps<TData> & { ref?: React.Ref<AgGridTableRef<TData>> }
) => React.ReactElement;
```

#### 步骤 2: 使用 useImperativeHandle 暴露方法

```typescript
React.useImperativeHandle(ref, () => ({
  setState: (state: TableState) => {
    const api = gridRef.current?.api;
    if (!api) return;

    // 应用列状态
    if (state.columnState) {
      api.applyColumnState({ state: state.columnState, applyOrder: true });
    }

    // 应用筛选
    if (state.filterModel !== undefined) {
      api.setFilterModel(state.filterModel);
    }

    // 刷新表头
    requestAnimationFrame(() => api.refreshHeader());
  },

  getState: () => {
    const api = gridRef.current?.api;
    if (!api) return { columnState: [], filterModel: null, sortModel: [] };

    const columnState = api.getColumnState();
    const filterModel = api.getFilterModel();
    const sortModel = columnState
      .filter((col) => col.sort)
      .map((col) => ({ colId: col.colId, sort: col.sort!, sortIndex: col.sortIndex }));

    return { columnState, filterModel, sortModel };
  },

  resetState: () => {
    const api = gridRef.current?.api;
    if (!api) return;
    api.resetColumnState();
    api.setFilterModel(null);
    api.sizeColumnsToFit();
  },

  sizeColumnsToFit: () => {
    gridRef.current?.api?.sizeColumnsToFit();
  },

  getGridApi: () => gridRef.current?.api ?? null,
}), []);
```

#### 步骤 3: 更新 index.ts 导出

```typescript
export { AgGridTable } from './ag-grid-table';
export type { AgGridTableProps, AgGridTableRef, TableState } from './ag-grid-table';
```

### 3. 使用示例

```tsx
import { AgGridTable, AgGridTableRef } from '@/components/ui/ag-grid-table';

function MyPage() {
  const tableRef = useRef<AgGridTableRef<MyData>>(null);

  // 切换视图时应用保存的状态
  const handleViewChange = (viewId: string) => {
    const savedState = getSavedViewState(viewId);
    tableRef.current?.setState(savedState);
  };

  // 保存当前视图
  const handleSaveView = () => {
    const currentState = tableRef.current?.getState();
    saveViewState(currentViewId, currentState);
  };

  // 重置表格
  const handleReset = () => {
    tableRef.current?.resetState();
  };

  return (
    <>
      <button onClick={handleReset}>重置</button>
      <AgGridTable ref={tableRef} ... />
    </>
  );
}
```

### 4. Storybook 测试用例

添加新的 Story 演示 ref API：

```tsx
export const WithRefApi: Story = {
  render: function Render(args) {
    const tableRef = useRef<AgGridTableRef>(null);
    const [log, setLog] = useState<string[]>([]);

    return (
      <div>
        <div className="flex gap-2 mb-4">
          <Button onClick={() => {
            const state = tableRef.current?.getState();
            setLog(prev => [...prev, `getState: ${JSON.stringify(state?.sortModel)}`]);
          }}>
            Get State
          </Button>
          <Button onClick={() => {
            tableRef.current?.setState({
              columnState: [{ colId: 'nav', sort: 'desc' }],
            });
            setLog(prev => [...prev, 'setState: applied desc sort on nav']);
          }}>
            Set Sort
          </Button>
          <Button onClick={() => {
            tableRef.current?.resetState();
            setLog(prev => [...prev, 'resetState: cleared']);
          }}>
            Reset
          </Button>
        </div>
        <AgGridTable ref={tableRef} {...args} />
        <pre className="mt-4 text-xs">{log.join('\n')}</pre>
      </div>
    );
  },
};
```

## 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `web/components/ui/ag-grid-table/ag-grid-table.tsx` | 添加 forwardRef + useImperativeHandle |
| `web/components/ui/ag-grid-table/index.ts` | 导出 AgGridTableRef 类型 |
| `web/stories/ui/ag-grid-table.stories.tsx` | 添加 WithRefApi story |

## 注意事项

1. **泛型 forwardRef**：TypeScript 的 forwardRef 不直接支持泛型，需要使用类型断言技巧
2. **Grid 未就绪处理**：所有 ref 方法需要检查 `gridRef.current?.api` 是否存在
3. **向后兼容**：现有 `initialState` 和 `onStateChange` props 保持不变
