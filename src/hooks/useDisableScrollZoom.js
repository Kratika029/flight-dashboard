import { useMapEvents } from 'react-leaflet';

const useDisableScrollZoom = () => {
  useMapEvents({
    wheel: (e) => {
      e.originalEvent.preventDefault();
    },
  });
};

export default useDisableScrollZoom;