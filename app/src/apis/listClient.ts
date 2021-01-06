import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import { ReqType, RespType } from '@/components/types';

const getFileList = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .get(`${API_URL}list`, {
        params: req,
      })
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const listClient = {
  getFileList,
};

export default listClient;
