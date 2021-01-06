<template>
  <a-layout id="layout">
    <a-layout-header id="layout-header">
      <a-space size="middle">
        <router-link
          :to="{ name: 'Layout' }"
          class="title"
        >
          {{ name }}
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
      {{ name }} created by
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
import { AxiosError } from 'axios';

import { Route } from 'ant-design-vue/lib/breadcrumb/Breadcrumb';
import {
  DeleteOutlined,
  FolderAddOutlined,
  GithubOutlined,
  RightOutlined,
} from '@ant-design/icons-vue';

import { FileList } from '@/components';
import { FileType, RespType } from '@/components/types';
import { listClient } from '@/apis';

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
      name: 'Naive-FTP',
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
    title(): string {
      const separator = ' > ';
      const route = this.route_parts.slice(1).join(separator);
      return this.name + (route ? separator + route : '');
    },
    route_parts(): string[] {
      const re = /^\/?|\/?$/g;
      const parts = this.$route.path.replaceAll(re, '').split('/');
      return parts;
    },
    routes(): Route[] {
      const parts = this.route_parts;
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
    $route: function () {
      const re = /^\/files\//;
      if (this.$route.path.match(re)) this.fetch();
    },
  },
  created() {
    this.fetch();
  },
  methods: {
    fetch() {
      this.loading = true;
      const re = /^\/?files\/?/;
      const path: string = this.$route.path.replace(re, '');
      listClient
        .getFileList({ path })
        .then((resp: RespType) => {
          this.loading = false;
          if (resp.data) this.fileList = resp.data;
          document.title = this.title;
        })
        .catch((err: AxiosError) => {
          this.loading = false;
          this.$router.replace({
            name: 'ErrorPage',
            params: this.parse_error(err),
          });
        });
    },
    parse_error(err: AxiosError) {
      let status = 504;
      let msg = 'Gateway Timeout';
      if (err.response) {
        if (err.response.status) {
          status = err.response.status;
        }
        if (err.response.data) {
          msg = err.response.data;
        } else if (err.response.statusText) {
          msg = err.response.statusText;
        }
      }
      return { status, msg };
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
