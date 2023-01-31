To log RSSI values for research purposes, use the cs_rssi_neighbour_parser.py and cs_rssi_extract_features.py scripts in the `crownstone_devtools/rssi` folder of this repository.

If you are interested in higher frequency data, check the configuration parameters of `inlude/localisation/cs_MeshTopology.h` in the bluenet firmware.

Dataflow is as indicated in the following sequence diagram.

```mermaid
sequenceDiagram
   participant H as Host PC
   participant D as Dev board
   participant A as Crownstone A
   participant B as Crownstone B
   Note right of H: UART
   Note over D,B: BLE Mesh
   rect rgb(191, 223, 255)
   B->>A: any mesh message type
   A->>A: MeshTopology::updateNeighbour
   end
   rect rgb(223, 191, 223)
   alt A has known neighbour data available
   A->>A: MeshTopology::onTickSecond<br>every 10 seconds or 5 minutes
   A->>D: MeshTopology::onMeshMsg<br>CS_MESH_MODEL_TYPE_NEIGHBOUR_RSSI
   D->>H: MeshTopology::sendRssiToUart<br>UART_OPCODE_TX_NEIGHBOUR_RSSI
   H->>H: cs_rssi_neighbour_parser.py<br>stores RSSI record in csv file
   else A has no data available
   A->>A: MeshTopology::onTickSecond<br>every 10 seconds or 5 minutes
   A->>D: MeshTopology::onMeshMsg<br>CS_MESH_MODEL_TYPE_CMD_NOOP
   end
   end
```
