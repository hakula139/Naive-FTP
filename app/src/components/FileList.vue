<template>
  <a-table
    :columns="columns"
    :data-source="data"
    :pagination="false"
    :row-key="rowKey"
    :row-selection="{
      selectedRowKeys: selected,
      onChange: onSelectChange,
    }"
  >
    <template #name="{ text, record }">
      <router-link
        v-if="record.fileType === 'Dir'"
        :to="`${text}/`"
      >
        <b>
          {{ text }}
        </b>
      </router-link>
      <span v-else>
        {{ text }}
      </span>
    </template>
    <template #perms="{ text }">
      <code>
        {{ text }}
      </code>
    </template>
  </a-table>
</template>

<script lang="ts">
import { defineComponent, PropType } from 'vue';
import { FileType } from '@/components/types';

const columns = [
  {
    title: 'Name',
    dataIndex: 'fileName',
    ellipsis: true,
    sorter: (a: FileType, b: FileType) => a.fileName.localeCompare(b.fileName),
    sortDirections: ['ascend', 'descend'],
    slots: { customRender: 'name' },
  },
  {
    title: 'Size',
    dataIndex: 'fileSize',
    width: '10%',
    align: 'right',
    ellipsis: true,
  },
  {
    title: 'Type',
    dataIndex: 'fileType',
    width: '10%',
    align: 'right',
    ellipsis: true,
  },
  {
    title: 'Modified time',
    dataIndex: 'modTime',
    width: '20%',
    align: 'right',
    ellipsis: true,
    sorter: (a: FileType, b: FileType) => a.modTime.localeCompare(b.modTime),
    sortDirections: ['descend', 'ascend'],
  },
  {
    title: 'Permissions',
    dataIndex: 'perms',
    width: '15%',
    align: 'right',
    ellipsis: true,
    slots: { customRender: 'perms' },
  },
  {
    title: 'Owner',
    dataIndex: 'owner',
    width: '10%',
    align: 'right',
    ellipsis: true,
  },
];

export default defineComponent({
  props: {
    data: {
      type: Array as PropType<FileType[]>,
      required: true,
    },
    selected: {
      type: Array as PropType<string[]>,
      default: [],
    },
  },
  emits: {
    'update:selected': null,
  },
  data() {
    return {
      columns,
      rowKey: 'fileName',
    };
  },
  methods: {
    onSelectChange(selectedRowKeys: string[]) {
      this.$emit('update:selected', selectedRowKeys);
    },
  },
});
</script>

<style lang="scss" scoped></style>
