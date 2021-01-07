import { createApp } from 'vue';

import App from './App.vue';
import './registerServiceWorker';
import router from './router';

import {
  Breadcrumb,
  Button,
  Empty,
  Input,
  Layout,
  Modal,
  Space,
  Table,
} from 'ant-design-vue';

const app = createApp(App);
app.use(router);

// Ant Design
app
  .use(Breadcrumb)
  .use(Button)
  .use(Empty)
  .use(Input)
  .use(Layout)
  .use(Modal)
  .use(Space)
  .use(Table);

app.mount('#app');
