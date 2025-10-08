import { useEffect, useState } from 'react';

export const useTypingAnimation = (message: string, speed: number = 5) => {
  const [animatedText, setAnimatedText] = useState('');

  useEffect(() => {
    let current = '';
    let i = 0;

    const typeNext = () => {
      if (i < message.length) {
        current += message[i++];
        setAnimatedText(current);
        setTimeout(typeNext, speed);
      }
    };

    typeNext();
  }, [message, speed]);

  return animatedText;
};
