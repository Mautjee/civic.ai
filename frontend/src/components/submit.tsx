import { FC, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { toast } from "sonner";
import { useMessage } from "@/hooks/messages";

export const Submit: FC = () => {
  const [message, setMessage] = useState("");
  const { data, error, mutate } = useMessage();

  const onSubmit = () => {
    console.log(message);
    mutate(message);
    toast("Message sent");
  };

  if (error) {
    return <div>Error: {error.message}</div>;
  }
  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <div className="w-full h-full flex flex-col justify-center items-center gap-4">
      <Textarea onChange={(e) => setMessage(e.target.value)} />
      <Button onClick={onSubmit}>Submit</Button>
    </div>
  );
};
