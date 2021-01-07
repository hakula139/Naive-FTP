<!--prettier-ignore-->
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
        <p>{{ modal.content }}</p>
        <a-input
          v-if="modal.input"
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
        input: true,
        title: '',
        content: '',
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
        input: true,
        title: 'Upload',
        content: 'Please enter the absolute path to the file.',
        data: '',
        placeholder: 'D:\\absolute\\path\\to\\the\\file',
        onModalOk: this.upload,
      };
    },
    onFolderAddClick() {
      this.modal = {
        visible: true,
        loading: false,
        input: true,
        title: 'New folder',
        content: 'Please enter the folder name.',
        data: '',
        placeholder: 'new_folder_name',
        onModalOk: this.mkdir,
      };
    },
    onDeleteClick() {
      this.modal = {
        visible: true,
        loading: false,
        input: false,
        title: 'Delete',
        content:
          'Are you sure you want to delete these files? ' +
          'Folders will be recursively removed. ' +
          'Press OK to continue.',
        data: '',
        placeholder: '',
        onModalOk: this.recursivelyRemove,
      };
    },
    openNotification(type: string, description: string) {
      notification[type]({
        message: type.toUpperCase(),
        description,
      });
    },
    isValidName(folderName: string): boolean {
      // ~`!#$%^&*=[]\';,/{}|":<>? is not allowed in folder names
      const re = /[~`!#$%^&*=[\]\\';,/{}|":<>?]/g;
      return !re.test(folderName);
    },
    isDirectory(fileName: string): boolean {
      const fileList: FileType[] = this.fileList.data;
      const matched: FileType[] = fileList.filter(
        (entry) => entry.fileName === fileName
      );
      return matched[0] && matched[0].fileType === 'Dir';
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
          if (resp.data) {
            this.fileList.data = resp.data;
          }
          document.title = this.title;
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', `Failed to fetch list data`);
        })
        .finally(() => {
          this.fileList.loading = false;
        });
    },
    retrieve(fileName: string) {
      const path = this.path + fileName;
      fileClient
        .retrieve({ path })
        .then((resp: RespType) => {
          if (resp.msg) {
            this.openNotification('success', `File downloaded to ${resp.msg}`);
          }
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', `Failed to download ${fileName}`);
          this.fetch();
        });
    },
    upload() {
      const path = this.modal.data;
      if (!path) {
        this.openNotification('warning', 'File path should not be blank');
        return;
      }
      this.modal.loading = true;
      fileClient
        .store({ path })
        .then((resp: RespType) => {
          if (resp.msg) {
            this.openNotification('success', 'File uploaded');
          }
          this.fetch();
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', 'Failed to upload');
        })
        .finally(() => {
          this.modal.visible = false;
          this.modal.loading = false;
        });
    },
    mkdir() {
      const folderName = this.modal.data;
      if (!folderName) {
        this.openNotification('warning', 'Folder name should not be blank');
        return;
      }
      if (!this.isValidName(folderName)) {
        this.openNotification(
          'warning',
          'Folder name should not contain special characters'
        );
        return;
      }
      this.modal.loading = true;
      dirClient
        .mkdir({ path: folderName })
        .then((_resp: RespType) => {
          this.openNotification('success', 'New folder created');
          this.fetch();
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', 'Failed to create folder');
        })
        .finally(() => {
          this.modal.visible = false;
          this.modal.loading = false;
        });
    },
    rmdir(folderName: string) {
      const path = this.path + folderName;
      dirClient
        .rmdir({ path })
        .then((resp: RespType) => {
          if (resp.msg) {
            this.openNotification('success', `${folderName}/ deleted`);
          }
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', `Failed to delete ${folderName}/`);
        })
        .finally(() => {
          this.afterRemove();
        });
    },
    remove(fileName: string) {
      const path = this.path + fileName;
      fileClient
        .remove({ path })
        .then((resp: RespType) => {
          if (resp.msg) {
            this.openNotification('success', `${fileName} deleted`);
          }
        })
        .catch((_err: AxiosError) => {
          this.openNotification('error', `Failed to delete ${fileName}`);
        })
        .finally(() => {
          this.afterRemove();
        });
    },
    afterRemove() {
      if (this.fileList.selected.length) {
        this.recursivelyRemove();
      } else {
        this.fetch();
      }
    },
    recursivelyRemove() {
      this.modal.visible = false;
      this.modal.loading = false;
      this.fileList.loading = true;
      const entry = this.fileList.selected.pop();
      if (!entry) {
        this.fileList.loading = false;
        return;
      }
      if (this.isDirectory(entry)) {
        this.rmdir(entry);
      } else {
        this.remove(entry);
      }
    },
    parseError(err: AxiosError): { status: number; msg: string } {
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
