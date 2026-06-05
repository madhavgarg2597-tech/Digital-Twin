eval_questions = [
    {
        "question": "What is JEPA and how does it work?",
        "ground_truth": "JEPA (Joint Embedding Predictive Architecture) is a non-generative architecture proposed by Yann LeCun that learns to predict representations of inputs rather than the inputs themselves. It uses an encoder to map inputs to embeddings and a predictor to predict the embedding of a target from the embedding of a context, avoiding the need to reconstruct pixel-level details.",
        "expected_source_type": "research papers"
    },
    {
        "question": "Why does Yann LeCun think LLMs will not lead to AGI?",
        "ground_truth": "Yann LeCun believes LLMs are limited because they are trained on text only, which is a very low-bandwidth source of information compared to visual and sensory experience. They lack grounding in the physical world, cannot plan, and do not have a world model. Auto-regressive token prediction is fundamentally insufficient for true understanding.",
        "expected_source_type": "interviews"
    },
    {
        "question": "What is self-supervised learning according to Yann LeCun?",
        "ground_truth": "Self-supervised learning is a method where a system learns to predict parts of its input from other parts, without requiring human-labeled data. Yann LeCun considers it the dark matter of intelligence and believes it is the key to building machines that learn like humans and animals, forming rich internal representations of the world.",
        "expected_source_type": "blogs"
    },
    {
        "question": "What is Yann LeCun's position on open source AI?",
        "ground_truth": "Yann LeCun is a strong advocate for open-source AI. He believes AI platforms should be open because they will become the primary way people access information and interact with the digital world. Concentrating AI power in a few companies would be dangerous, and open source ensures diversity, safety through transparency, and democratic access.",
        "expected_source_type": "interviews"
    },
    {
        "question": "What are the main components of Yann LeCun's autonomous machine intelligence architecture?",
        "ground_truth": "Yann LeCun's proposed architecture for autonomous machine intelligence includes: a World Model that predicts future states, a Configurator module, a Perception module, a Short-Term Memory, a Cost module that computes energy/objectives, and an Actor module that plans and takes actions. The World Model is the central component.",
        "expected_source_type": "research papers"
    },
    {
        "question": "What is the difference between contrastive and non-contrastive self-supervised learning?",
        "ground_truth": "Contrastive methods like SimCLR learn by pulling positive pairs together and pushing negative pairs apart in embedding space. Non-contrastive methods like BYOL and VICReg avoid using negative pairs entirely, instead using techniques like redundancy reduction, stop gradients, or variance-covariance regularization to prevent representation collapse.",
        "expected_source_type": "research papers"
    },
    {
        "question": "What does Yann LeCun think about the existential risk of AI?",
        "ground_truth": "Yann LeCun is skeptical of claims that AI poses an imminent existential risk to humanity. He argues that current AI systems are far from human-level intelligence, and that fear-mongering about AI doom is counterproductive. He believes the real risks are more mundane, like bias, misuse, and concentration of power, and that open-source AI is the best safeguard.",
        "expected_source_type": "interviews"
    },
    {
        "question": "What is the role of energy-based models in Yann LeCun's vision of AI?",
        "ground_truth": "Energy-based models (EBMs) are central to LeCun's vision. They assign a scalar energy to each configuration of variables, with low energy for compatible configurations and high energy for incompatible ones. They provide a unified framework for both discriminative and generative tasks and avoid the need for explicit probability normalization.",
        "expected_source_type": "research papers"
    },
    {
        "question": "How does Yann LeCun's work on convolutional neural networks relate to modern deep learning?",
        "ground_truth": "Yann LeCun pioneered convolutional neural networks (CNNs) in the late 1980s with LeNet for handwritten digit recognition. CNNs introduced weight sharing, local connectivity, and pooling which became the foundation of modern deep learning for computer vision. His work directly inspired architectures like AlexNet, VGG, and ResNet.",
        "expected_source_type": "research papers"
    },
    {
        "question": "What is Yann LeCun's view on reinforcement learning?",
        "ground_truth": "Yann LeCun believes reinforcement learning alone is insufficient for building intelligent systems because it is extremely sample-inefficient. Animals and humans learn most of their knowledge through observation, not trial and error. He advocates for self-supervised learning combined with world models as a more scalable alternative.",
        "expected_source_type": "interviews"
    },
    {
        "question": "What is VICReg?",
        "ground_truth": "VICReg (Variance-Invariance-Covariance Regularization) is a self-supervised learning method that prevents representation collapse without using negative pairs. It works by maintaining three properties in the embedding space: variance (keeping features spread out), invariance (pulling augmented views together), and covariance (decorrelating feature dimensions).",
        "expected_source_type": "research papers"
    },
    {
        "question": "What does Yann LeCun think about the Turing Test?",
        "ground_truth": "Yann LeCun is critical of the Turing Test as a measure of intelligence. He argues it primarily tests linguistic competence rather than true understanding or intelligence. A system can fool humans with clever text generation without actually understanding the world or being able to reason and plan.",
        "expected_source_type": "interviews"
    },
    {
        "question": "How does the world model concept work in LeCun's framework?",
        "ground_truth": "The world model in LeCun's framework is a module that learns an internal representation of how the world works. It can predict future states of the world given current state and actions, enabling the system to plan by simulating outcomes mentally before acting. It learns primarily through self-supervised observation of the environment.",
        "expected_source_type": "research papers"
    },
    {
        "question": "What is Siamese network architecture and how did LeCun contribute to it?",
        "ground_truth": "Siamese networks use two identical subnetworks with shared weights to process two inputs and compare their representations. Yann LeCun and colleagues introduced this architecture for signature verification in the early 1990s. It became foundational for metric learning, face verification, and modern contrastive learning methods.",
        "expected_source_type": "research papers"
    },
    {
        "question": "What does Yann LeCun think is missing from current AI systems?",
        "ground_truth": "LeCun believes current AI systems lack a world model, the ability to plan, common sense understanding of the physical world, and hierarchical planning capabilities. They cannot reason about cause and effect, predict consequences of actions, or learn efficiently from limited data the way humans and animals do.",
        "expected_source_type": "blogs"
    },
]
