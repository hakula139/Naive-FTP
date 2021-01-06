<template>
  <a-layout id="layout">
    <a-layout-header id="layout-header">
      <a-space size="middle">
        <router-link
          :to="{ name: 'Layout' }"
          class="title"
        >
          {{ title }}
        </router-link>
        <a-button
          type="primary"
          shape="circle"
          size="large"
        >
          <template #icon>
            <FolderAddOutlined />
          </template>
        </a-button>
        <a-button
          v-if="hasSelected"
          type="danger"
          shape="circle"
          size="large"
        >
          <template #icon>
            <DeleteOutlined />
          </template>
        </a-button>
      </a-space>
      <a-space size="middle">
        <a-button
          type="primary"
          shape="circle"
          size="large"
          :href="links.repo"
          target="_blank"
        >
          <template #icon>
            <GithubOutlined />
          </template>
        </a-button>
      </a-space>
    </a-layout-header>
    <a-layout-content id="layout-content">
      <a-breadcrumb :routes="routes">
        <template #separator>
          <span class="path-separator">
            <RightOutlined />
          </span>
        </template>
        <template #itemRender="{ route }">
          <router-link :to="route.path">
            {{ route.breadcrumbName }}
          </router-link>
        </template>
      </a-breadcrumb>
      <file-list
        v-model:selected="selectedRowKeys"
        :data="fileList"
        :loading="loading"
      />
    </a-layout-content>
    <a-layout-footer id="layout-footer">
      {{ title }} created by
      <a
        :href="links.blog"
        target="_blank"
      >
        {{ author }}
      </a>
    </a-layout-footer>
  </a-layout>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

import { Route } from 'ant-design-vue/lib/breadcrumb/Breadcrumb';
import {
  DeleteOutlined,
  FolderAddOutlined,
  GithubOutlined,
  RightOutlined,
} from '@ant-design/icons-vue';

import { FileList } from '@/components';
import { FileType } from '@/components/types';
import { fileClient } from '@/apis';

export default defineComponent({
  components: {
    DeleteOutlined,
    FolderAddOutlined,
    GithubOutlined,
    RightOutlined,
    FileList,
  },
  data() {
    return {
      title: 'Naive-FTP',
      author: 'Hakula',
      links: {
        blog: 'https://hakula.xyz',
        repo: 'https://github.com/hakula139/Naive-FTP',
      },
      selectedRowKeys: [] as string[],
      fileList: [] as FileType[],
      loading: false,
    };
  },
  computed: {
    routes(): Route[] {
      const re = /^\/?|\/?$/g;
      const parts: string[] = this.$route.path.replaceAll(re, '').split('/');
      const breadcrumbs: Route[] = [];
      parts.forEach((part, i) => {
        const parentPath = i ? breadcrumbs[i - 1].path : '/';
        breadcrumbs.push({
          breadcrumbName: decodeURIComponent(part),
          path: `${parentPath}${part}/`,
        });
      });
      return breadcrumbs;
    },
    hasSelected(): boolean {
      return this.selectedRowKeys.length > 0;
    },
  },
  watch: {
    '$route': 'fetch',
  },
  created() {
    this.fetch();
  },
  methods: {
    fetch() {
      this.loading = true;
      const re = /^\/?files\/?/;
      const path: string = this.$route.path.replace(re, '');
      fileClient
        .getFileList({ path })
        .then((resp) => {
          this.loading = false;
          this.fileList = resp.data;
        })
        .catch(() => {
          this.loading = false;
          this.$router.push({ name: 'NotFound' });
        });
    },
  },
});
</script>

<style lang="scss" scoped>
#layout {
  min-height: 100vh;
}

#layout-header {
  position: fixed;
  z-index: 1;
  height: 64px;
  width: 100%;
  background-color: #d3a998;

  .ant-space {
    height: 64px;

    &:last-of-type {
      float: right;
    }
  }

  .title {
    margin-right: 16px;
    color: #e6fffb;
    font-size: 2em;
  }
}

#layout-content {
  margin-top: 64px;
  padding: 0 50px;

  .ant-breadcrumb {
    margin: 20px 0;

    a {
      font-size: 1.5em;
    }

    > span:last-child a {
      font-weight: bolder;
    }

    .path-separator {
      margin: 0 4px;
    }
  }
}

#layout-footer {
  text-align: center;
  font-size: 16px;
}
</style>
