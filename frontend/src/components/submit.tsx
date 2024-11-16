import { useMutation } from "@tanstack/react-query";
import { FC } from "react";
import { useMessage } from "../hooks/messages";

export const Submit: FC = () => {
  const { data, mutate } = useMessage();
  return (
    <div>
      <div></div>
    </div>
  );
};
