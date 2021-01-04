<template>
  <a-table
    :columns="columns"
    :data-source="data"
    :row-selection="rowSelection"
    :scroll="scroll"
  >
    <template #name="{ text }"> {{ text.first }} {{ text.last }} </template>
  </a-table>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { ColumnProps } from 'ant-design-vue/lib/table/interface';
import { FileType } from '@/components/types';

const columns: ColumnProps[] = [
  {
    title: 'Name',
    dataIndex: 'fileName',
    sorter: (a: FileType, b: FileType) => a.fileName < b.fileName,
    sortDirections: ['ascend', 'descend'],
    defaultSortOrder: 'ascend',
    width: '30%',
    ellipsis: true,
  },
  {
    title: 'Size',
    dataIndex: 'fileSize',
    width: '12%',
    ellipsis: true,
  },
  {
    title: 'Type',
    dataIndex: 'fileType',
    width: '8%',
    ellipsis: true,
  },
  {
    title: 'Modified time',
    dataIndex: 'modTime',
    width: '25%',
    ellipsis: true,
  },
  {
    title: 'Permissions',
    dataIndex: 'perms',
    width: '15%',
    ellipsis: true,
  },
  {
    title: 'Owner',
    dataIndex: 'owner',
    width: '10%',
    ellipsis: true,
  },
];

export default defineComponent({
  props: {
    data: {
      type: Array as PropType<FileType[]>,
      required: true,
    },
  },
  data() {
    return {
      columns,
      rowSelection: {},
      scroll: { y: true },
    };
  },
});
</script>

<style lang="scss" scoped></style>
