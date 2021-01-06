import axios, { AxiosError, AxiosResponse } from 'axios';
import { API_URL } from '@/utils/config';
import FileType from '@/components/types/file';

interface FileListReq {
  // File path
  path: string;
}

interface FileListResp {
  // Server status code
  status_code: number;
  // Server response message
  msg: string;
  // File list data
  data: FileType[];
}

const getFileList = (req: FileListReq): Promise<FileListResp> =>
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

const fileClient = {
  getFileList,
};

export default fileClient;
