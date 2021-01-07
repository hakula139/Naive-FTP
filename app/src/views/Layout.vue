<template>
  <a-layout id="layout">
    <a-layout-header id="layout-header">
      <a-space size="middle">
        <router-link
          to="/files/"
          class="title"
        >
          {{ name }}
        </router-link>
        <a-button
          type="primary"
          shape="circle"
          size="large"
          @click="onUploadClick"
        >
          <template #icon>
            <UploadOutlined />
          </template>
        </a-button>
        <a-button
          type="primary"
          shape="circle"
          size="large"
          @click="onFolderAddClick"
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
          @click="onDeleteClick"
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
      <a-breadcrumb :routes="breadcrumbs">
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
        v-model:selected="fileList.selected"
        :data="fileList.data"
        :loading="fileList.loading"
        @retrieve="retrieve"
      />
      <a-modal
        v-model:visible="modal.visible"
        :title="modal.title"
        :confirm-loading="modal.loading"
        @ok="modal.onModalOk"
      >
        <p>{{ modal.text }}</p>
        <a-input
          v-model:value="modal.data"
          :placeholder="modal.placeholder"
          allow-clear
        />
      </a-modal>
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

import { notification } from 'ant-design-vue';
import { Route } from 'ant-design-vue/lib/breadcrumb/Breadcrumb';
import {
  DeleteOutlined,
  FolderAddOutlined,
  GithubOutlined,
  RightOutlined,
  UploadOutlined,
} from '@ant-design/icons-vue';

import { FileList } from '@/components';
import { FileType, RespType } from '@/components/types';
import { fileClient, dirClient } from '@/apis';

export default defineComponent({
  components: {
    DeleteOutlined,
    FolderAddOutlined,
    GithubOutlined,
    RightOutlined,
    UploadOutlined,
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
      fileList: {
        data: [] as FileType[],
        selected: [] as string[],
        loading: false,
      },
      modal: {
        visible: false,
        loading: false,
        title: '',
        text: '',
        data: '',
        placeholder: '',
        onModalOk: Function(),
      },
    };
  },
  computed: {
    title(): string {
      const separator = ' > ';
      const route = this.routeParts.slice(1).join(separator);
      return this.name + (route ? separator + route : '');
    },
    path(): string {
      const re = /^\/?files/;
      const path = this.$route.path.replace(re, '');
      return path;
    },
    routeParts(): string[] {
      const re = /^\/?|\/?$/g;
      const parts = this.$route.path.replaceAll(re, '').split('/');
      return parts;
    },
    breadcrumbs(): Route[] {
      const parts = this.routeParts;
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
      return this.fileList.selected.length > 0;
    },
  },
  watch: {
    $route: function () {
      const re = /^\/files\//;
      if (this.$route.path.match(re)) this.changeDirectory();
    },
  },
  created() {
    this.changeDirectory();
  },
  methods: {
    onUploadClick() {
      this.modal = {
        visible: true,
        loading: false,
        title: 'Upload',
        text: 'Please enter the absolute path to the file.',
        data: '',
        placeholder: 'D:\\absolute\\path\\to\\the\\file',
        onModalOk: this.upload,
      };
    },
    onFolderAddClick() {
      // TODO: mkdir
      return;
    },
    onDeleteClick() {
      // TODO: delete, rmdir
      return;
    },
    openNotification(type: string, description: string) {
      notification[type]({
        message: type.toUpperCase(),
        description,
      });
    },
    changeDirectory() {
      this.fileList.loading = true;
      dirClient
        .cwd({ path: this.path })
        .then((_resp: RespType) => {
          this.fetch();
        })
        .catch((err: AxiosError) => {
          this.$router.push({
            name: 'ErrorPage',
            params: this.parseError(err),
          });
        });
    },
    fetch() {
      this.fileList.loading = true;
      dirClient
        .list({ path: this.path })
        .then((resp: RespType) => {
          this.fileList.loading = false;
          if (resp.data) this.fileList.data = resp.data;
          document.title = this.title;
        })
        .catch((err: AxiosError) => {
          this.$router.push({
            name: 'ErrorPage',
            params: this.parseError(err),
          });
        });
    },
    retrieve(fileName: string) {
      fileClient
        .retrieve({ path: this.path + fileName })
        .then((resp: RespType) => {
          if (resp.msg) {
            this.openNotification('success', `File downloaded to ${resp.msg}`);
          }
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', 'File download failed');
          this.fetch();
        });
    },
    upload() {
      if (!this.modal.data) {
        this.openNotification('warning', 'File path should not be blank');
        return;
      }
      this.modal.loading = true;
      this.modal.text = 'Uploading... Please wait.';
      fileClient
        .store({ path: this.modal.data })
        .then((_resp: RespType) => {
          this.openNotification('success', 'File upload success');
          this.fetch();
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', 'File upload failed');
        })
        .finally(() => {
          this.modal.visible = false;
          this.modal.loading = false;
        });
    },
    mkdir() {
      return;
    },
    remove() {
      return;
    },
    parseError(err: AxiosError) {
      let status = 504;
      let msg = 'Gateway Timeout';
      if (err.response) {
        if (err.response.status) {
          status = err.response.status;
        }
        if (err.response.statusText) {
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
