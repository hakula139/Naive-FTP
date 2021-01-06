import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import { ReqType, RespType } from '@/components/types';

const dirApiUrl = API_URL + 'dir';

const list = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .get(dirApiUrl, {
        params: req,
      })
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const cwd = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .post(dirApiUrl, req)
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const mkdir = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .put(dirApiUrl, req)
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const dirClient = {
  list,
  cwd,
  mkdir,
};

export default dirClient;
