import { motion } from "framer-motion";

interface Props {
  loading?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

export default function PrimaryButton({
  loading,
  onClick,
  children,
}: Props) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      disabled={loading}
      onClick={onClick}
      className="
      rounded-xl
      bg-cyan-500
      px-7
      py-3
      font-semibold
      text-black
      transition
      hover:bg-cyan-400
      disabled:opacity-50
      "
    >
      {loading ? "Verifying..." : children}
    </motion.button>
  );
}