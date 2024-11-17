import { Auth } from "@/components/auth";
import { Submit } from "@/components/submit";
import { FC, useState } from "react";

export const Landing: FC = () => {
  const [auth, setAuth] = useState(false);

  if (!auth) return <Auth setAuth={setAuth} />;

  return <Submit />;
};
