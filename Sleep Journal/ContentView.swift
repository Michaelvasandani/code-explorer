// -------------------------------------------------------------------------
// This item is the property of ResMed Ltd, and contains confidential and trade
// secret information. It may not be transferred from the custody or control of
// ResMed except as authorized in writing by an officer of ResMed. Neither this
// item nor the information it contains may be used, transferred, reproduced,
// published, or disclosed, in whole or in part, and directly or indirectly,
// except as expressly authorized by an officer of ResMed, pursuant to written
// agreement.
//
// Copyright (c) 2026 ResMed Ltd.  All rights reserved.
//-------------------------------------------------------------------------

import SwiftUI
import UIKit

struct ContentView: View {
    var body: some View {
        RootNavigationControllerRepresentable()
            .ignoresSafeArea()
    }
}

private struct RootNavigationControllerRepresentable: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UINavigationController {
        let root = SleepJournalListViewController()
        return UINavigationController(rootViewController: root)
    }

    func updateUIViewController(_ uiViewController: UINavigationController, context: Context) {}
}

#Preview {
    ContentView()
}
