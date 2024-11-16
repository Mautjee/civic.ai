import { FC, useState } from "react";
import { Textarea } from "./ui/textarea";
import { Button } from "./ui/button";
import { toast } from "sonner";
export const Submit: FC = () => {
  const [message, setMessage] = useState("");

  const onSubmit = () => {
    console.log(message);
    toast("Message sent");
  };
  return (
    <div className="w-full h-full flex flex-col justify-center items-center gap-4">
      <Textarea onChange={(e) => setMessage(e.target.value)} />
      <Button onClick={onSubmit}>Submit</Button>
    </div>
  );
};
