import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import { ReqType, RespType } from '@/components/types';

const retrieve = (req: ReqType): Promise<RespType> =>
  new Promise((resolve, reject) => {
    axios
      .get(`${API_URL}retrieve`, {
        params: req,
      })
      .then((resp: AxiosResponse) => {
        resolve(resp.data);
      })
      .catch((err: AxiosError) => reject(err));
  });

const commonClient = {
  retrieve,
};

export default commonClient;
