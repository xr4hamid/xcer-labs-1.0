// src/FloatingIcon.js
import React from "react";
import { Bot } from "lucide-react"; // chatbot icon
import { motion } from "framer-motion";

const FloatingIcon = ({ onClick }) => {
  return (
    <motion.div
      initial={{ scale: 0 }}
      animate={{ scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      className="fixed bottom-6 right-6 z-50"
    >
      <button
        onClick={onClick}
        className="bg-black text-white dark:bg-white dark:text-black rounded-full p-4 shadow-xl hover:scale-105 hover:rotate-6 transition-all"
      >
        <Bot className="w-6 h-6" />
      </button>
    </motion.div>
  );
};

export default FloatingIcon;
