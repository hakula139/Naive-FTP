import axios from 'axios';
import { API_URL } from '@/utils/config';
import FileType from '@/components/types/file';

interface FileReq {
  // File path
  path: string;
}

interface FileResp {
  // Server status code
  status: number;
  // Server response message
  msg: string;
  // File list data
  data: FileType[];
}

const getFileList = (req: FileReq): Promise<FileResp> =>
  new Promise((resolve, reject) => {
    axios
      .get(`${API_URL}/list`, {
        params: req,
      })
      .then((resp) => {
        resolve(resp.data);
      })
      .catch((err) => reject(err));
  });

const fileClient = {
  getFileList,
};

export default fileClient;
