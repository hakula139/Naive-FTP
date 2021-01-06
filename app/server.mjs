import compression from 'compression';
import history from 'connect-history-api-fallback';
import cors from 'cors';
import express from 'express';
import favicon from 'serve-favicon';
import path from 'path';

const app = express();
const distPath = path.resolve('dist');
const listen_port = 8181;

app
  .use(compression())
  .use(cors())
  .use(favicon(path.join(distPath, 'favicon.ico')))
  .use(history())
  .use(express.static(distPath))
  .listen(listen_port, () => {
    console.log('Welcome to Naive-FTP client handler! Press CTRL+C to exit.');
    console.log('Listening at port', listen_port);
  });
