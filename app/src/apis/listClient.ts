import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import FileType from '@/components/types/file';

export interface ListReq {
  // File path
  path: string;
}

export interface ListResp {
  // Server status code
  status_code: number;
  // Server response message
  msg: string;
  // File list data
  data: FileType[];
}

const getFileList = (req: ListReq): Promise<ListResp> =>
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
