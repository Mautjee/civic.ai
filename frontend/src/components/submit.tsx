import { FC } from "react";
import { useMessage } from "../hooks/messages";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";

export const Submit: FC = () => {
  const { data, mutate } = useMessage();
  return (
    <div className="w-full h-full flex flex-col gap-4">
      <Textarea value={data} onChange={(e) => mutate(e.target.value)} />
      <Button>Submit</Button>
    </div>
  );
};
