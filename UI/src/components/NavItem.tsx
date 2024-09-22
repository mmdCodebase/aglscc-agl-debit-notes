import { forwardRef } from "react";
import { useLocation } from "react-router-dom";
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from "@mui/material";

type Props = {
  open: boolean;
  path: string;
  itemText: string;
  itemIcon: React.ReactNode;
};

const NavItem = forwardRef<HTMLDivElement, Props>(
  ({ open, path, itemText, itemIcon, ...other }, ref) => {
    const location = useLocation();

    return (
      <div ref={ref} {...other}>
        <ListItem key={path} disablePadding sx={{ display: "block" }}>
          <ListItemButton
            selected={location.pathname === path ? true : false}
            sx={{
              minHeight: 48,
              justifyContent: open ? "initial" : "center",
              px: 2.5,
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 0,
                mr: open ? 3 : "auto",
                justifyContent: "center",
              }}
            >
              {itemIcon}
            </ListItemIcon>
            <ListItemText primary={itemText} sx={{ opacity: open ? 1 : 0 }} />
          </ListItemButton>
        </ListItem>
      </div>
    );
  }
);

export default NavItem;
