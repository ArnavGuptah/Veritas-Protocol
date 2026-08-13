import {
    createBrowserRouter,
} from "react-router-dom";

import Home from "../pages/Home";
import Result from "../pages/Result";

export const router = createBrowserRouter([
    {
        path: "/",
        element: <Home />,
    },
    {
        path: "/result/:id",
        element: <Result />,
    },
]);