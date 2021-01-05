import { createApp } from 'vue';

import App from './App.vue';
import './registerServiceWorker';
import router from './router';

import {
  Breadcrumb,
  Button,
  Layout,
  Space,
  Table,
} from 'ant-design-vue';

const app = createApp(App);
app.use(router);

// Ant Design
app
  .use(Breadcrumb)
  .use(Button)
  .use(Layout)
  .use(Space)
  .use(Table);

app.mount('#app');
