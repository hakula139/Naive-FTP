import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import { ReqType, RespType } from '@/components/types';

const fileApiUrl = API_URL + 'file';

const retrieve = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .get(fileApiUrl, {
        params: req,
      })
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const store = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .put(fileApiUrl, req)
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const remove = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .delete(fileApiUrl, {
        data: req,
      })
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const fileClient = {
  retrieve,
  store,
  remove,
};

export default fileClient;
