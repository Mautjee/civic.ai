import { UseMutationResult, useMutation } from "@tanstack/react-query";
import { messageApi } from "../api";
import { Message } from "@/types/messages";

export const useMessage = (
  message?: string,
): UseMutationResult<Message, Error, void, unknown> => {
  return useMutation<Message, Error>({
    mutationKey: ["messagePost", message],
    mutationFn: messageApi.postMessage,
  });
};
