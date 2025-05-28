import { createContext, useContext } from 'react';

const AuthContext = createContext({
  user: null,
  tokens: null,
  groups: [],
  logout: () => {},
  loading: true,
});

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
