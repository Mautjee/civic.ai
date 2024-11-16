import { UseMutationResult, useMutation } from "@tanstack/react-query";
import { messageApi } from "../api";

export const useMessage = (
  message?: string,
): UseMutationResult<string, Error, void, unknown> => {
  return useMutation<string, Error>({
    mutationKey: ["messagePost", message],
    mutationFn: messageApi.postMessage,
  });
};
