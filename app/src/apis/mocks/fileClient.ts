import { FileType } from '@/components/types';
import { mockFileList } from '@/mocks';

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

// FIXME: mock
const getFileList = (_req: FileReq): Promise<FileResp> =>
  new Promise((resolve) => {
    resolve({
      status: 200,
      msg: 'Success.',
      data: mockFileList,
    });
  });

const fileClient = {
  getFileList,
};

export default fileClient;
