import CoreLocation
import Foundation

final class DeviceLocationProvider: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var continuation: CheckedContinuation<CLLocationCoordinate2D?, Never>?

    override init() {
        super.init()
        manager.delegate = self
    }

    func requestSingleLocation() async -> CLLocationCoordinate2D? {
        let status = manager.authorizationStatus
        if status == .denied || status == .restricted {
            return nil
        }

        return await withCheckedContinuation { continuation in
            self.continuation = continuation
            manager.requestWhenInUseAuthorization()
            manager.requestLocation()
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        continuation?.resume(returning: locations.first?.coordinate)
        continuation = nil
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        continuation?.resume(returning: nil)
        continuation = nil
    }
}
